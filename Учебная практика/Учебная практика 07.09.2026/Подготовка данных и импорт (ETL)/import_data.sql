\set ON_ERROR_STOP on

\copy partners (partner_id, company_name, inn, contact_email, phone, rating) FROM 'import_partners_clean.csv' WITH (FORMAT csv, HEADER true, DELIMITER ',', ENCODING 'UTF8', NULL '');

-- После COPY счётчик-последовательность осталась на нуле,
-- а у нас уже есть явные id до 3. Сбрасываем последовательность,
-- чтобы следующие вставки не получили конфликтующие id.
SELECT setval('partners_partner_id_seq', (SELECT COALESCE(MAX(partner_id), 0) FROM partners));

-- Загружаем продажи во временную таблицу.
-- В исходных данных вместо product_id стоит product_name,
-- поэтому храним название.

DROP TABLE IF EXISTS tmp_sales_raw;
CREATE TEMP TABLE tmp_sales_raw (
    sale_id      INT,
    partner_id   INT,
    product_name VARCHAR(255),
    sale_date    DATE,
    quantity     INT,
    total_amount DECIMAL(12,2)
);

\copy tmp_sales_raw (sale_id, partner_id, product_name, sale_date, quantity, total_amount) FROM 'import_sales_clean.txt' WITH (FORMAT csv, HEADER true, DELIMITER E'\t', ENCODING 'UTF8', NULL '');

-- Заполняем таблицу продуктов уникальными товарами.
-- base_price берём как цену за штуку (total_amount / quantity).
-- ON CONFLICT защищает от повторного добавления, если товар уже есть.

INSERT INTO products (product_name, unit, base_price)
SELECT DISTINCT
    product_name,
    'шт.'  AS unit,
    (total_amount / quantity) AS base_price
FROM tmp_sales_raw
ON CONFLICT (product_name) DO NOTHING;

-- Переносим продажи в основную таблицу.
-- product_id подставляем из справочника по названию продукта,
-- unit_price пересчитываем как total_amount / quantity.
-- Дополнительное условие WHERE отсекает строки с партнёрами,
-- которых нет в partners (на всякий случай).

INSERT INTO sales (sale_id, partner_id, product_id, sale_date, quantity, unit_price, total_amount)
SELECT
    s.sale_id,
    s.partner_id,
    p.product_id,
    s.sale_date,
    s.quantity,
    (s.total_amount / s.quantity) AS unit_price,
    s.total_amount
FROM tmp_sales_raw s
JOIN products p ON p.product_name = s.product_name
WHERE s.partner_id IN (SELECT partner_id FROM partners);

-- Временная таблица больше не нужна - удаляем её сразу.
DROP TABLE tmp_sales_raw;

-- Так же сбрасываем последовательность счётчика sale_id.
SELECT setval('sales_sale_id_seq', (SELECT COALESCE(MAX(sale_id), 0) FROM sales));

-- Шаг 5. Проверочные запросы: сколько строк в каждой таблице.
-- (должно получиться partners=3, products=3, sales=4)

SELECT 'partners' AS table_name, COUNT(*) AS row_count FROM partners
UNION ALL
SELECT 'products', COUNT(*) FROM products
UNION ALL
SELECT 'sales', COUNT(*) FROM sales;
