-- 1. Количество строк в каждой таблице
SELECT 'partners' AS table_name, COUNT(*) AS row_count FROM partners
UNION ALL
SELECT 'products', COUNT(*) FROM products
UNION ALL
SELECT 'sales', COUNT(*) FROM sales;

-- 2. Проверка партнеров
SELECT partner_id, company_name, inn, contact_email, phone, rating
FROM partners
ORDER BY partner_id;

-- 3. Проверка продуктов
SELECT product_id, product_name, unit, base_price
FROM products
ORDER BY product_id;

-- 4. Проверка продаж (с join для читаемости)
SELECT
    s.sale_id,
    pr.company_name AS partner,
    p.product_name,
    s.sale_date,
    s.quantity,
    s.unit_price,
    s.total_amount
FROM sales s
JOIN partners pr ON pr.partner_id = s.partner_id
JOIN products p ON p.product_id = s.product_id
ORDER BY s.sale_id;

-- 5. Проверка ограничений (constraint violations - должно вернуть 0 строк)
-- Проверка CHECK total_amount ≈ quantity * unit_price
-- (допуск на округление: unit_price хранится с точностью до копейки,
--  поэтому итог может отличаться не более чем на quantity * 0.005)
SELECT 'sales chk_total_amount' AS check_name, COUNT(*) AS violations
FROM sales
WHERE ABS(total_amount - quantity * unit_price) >= 0.005 * quantity

UNION ALL
-- Проверка rating range
SELECT 'partners rating range', COUNT(*)
FROM partners
WHERE rating IS NOT NULL AND (rating < 0 OR rating > 5)

UNION ALL
-- Проверка quantity > 0
SELECT 'sales quantity > 0', COUNT(*)
FROM sales
WHERE quantity <= 0

UNION ALL
-- Проверка внешних ключей (если FK отключены)
SELECT 'sales orphan partner_id', COUNT(*)
FROM sales s
LEFT JOIN partners pr ON pr.partner_id = s.partner_id
WHERE pr.partner_id IS NULL

UNION ALL
SELECT 'sales orphan product_id', COUNT(*)
FROM sales s
LEFT JOIN products p ON p.product_id = s.product_id
WHERE p.product_id IS NULL;
