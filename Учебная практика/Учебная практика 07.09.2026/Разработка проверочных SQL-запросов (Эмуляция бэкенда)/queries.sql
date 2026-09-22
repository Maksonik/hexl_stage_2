-- 1. Список партнеров с количеством доставок (LEFT JOIN + COUNT)
-- Сортировка по названию компании
SELECT
    p.partner_id,
    p.company_name,
    p.inn,
    p.contact_email,
    p.phone,
    p.rating,
    COUNT(s.sale_id) AS deliveries_count
FROM partners p
LEFT JOIN sales s ON s.partner_id = p.partner_id
GROUP BY p.partner_id, p.company_name, p.inn, p.contact_email, p.phone, p.rating
ORDER BY p.company_name;


-- 2. Транзакция: создание нового партнера + первая тестовая доставка

BEGIN;

-- Убираем данные прошлого запуска, чтобы скрипт можно было выполнять повторно
DELETE FROM sales
WHERE partner_id = (SELECT partner_id FROM partners WHERE inn = '7709999999');

DELETE FROM partners
WHERE inn = '7709999999';

WITH new_partner AS (
    INSERT INTO partners (company_name, inn, contact_email, phone, rating)
    VALUES ('ООО "Новый Партнер"', '7709999999', 'new_partner@example.com', '+7 (900) 000-00-00', 5.00)
    RETURNING partner_id
)
INSERT INTO sales (partner_id, product_id, sale_date, quantity, unit_price, total_amount)
SELECT
    np.partner_id,
    (SELECT product_id FROM products ORDER BY product_id LIMIT 1),
    CURRENT_DATE,
    10,
    500.00,
    5000.00
FROM new_partner np;

COMMIT;


-- 3. История отгрузок конкретного партнера за период
-- Параметры: partner_id (int), start_date (date), end_date (date)
-- Используем PREPARE/EXECUTE для демонстрации параметризованного запроса.

PREPARE shipment_history (int, date, date) AS
SELECT
    p.product_name,
    s.sale_date,
    s.quantity,
    s.unit_price,
    s.total_amount
FROM sales s
JOIN products p ON p.product_id = s.product_id
WHERE s.partner_id = $1
  AND s.sale_date BETWEEN $2 AND $3
ORDER BY s.sale_date, p.product_name;

-- Пример: история партнёра 1 за март 2026
EXECUTE shipment_history(1, '2026-03-01', '2026-03-31');

DEALLOCATE shipment_history;
