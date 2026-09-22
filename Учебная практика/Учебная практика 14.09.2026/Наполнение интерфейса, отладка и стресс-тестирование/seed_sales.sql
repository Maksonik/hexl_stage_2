-- Дополнительные продажи для демонстрации разных уровней скидки.
-- Идемпотентный скрипт: сначала удаляет свои строки, затем вставляет заново.
-- total_amount = quantity * unit_price (проходит CHECK chk_total_amount).

DELETE FROM sales WHERE sale_id BETWEEN 500 AND 599;
DELETE FROM partners WHERE inn = '7702000005';

-- Партнер без истории продаж: итог SUM = NULL -> скидка 0%
INSERT INTO partners (partner_id, company_name, inn, contact_email, phone, rating)
VALUES (5, 'ООО "Партнер без истории"', '7702000005', 'no_history@example.com', '+7 (900) 111-22-33', 4.00);

-- Партнер 1: объем доводим до 60 000 шт. (скидка 10%)
INSERT INTO sales (sale_id, partner_id, product_id, sale_date, quantity, unit_price, total_amount)
VALUES
    (500, 1, 2, '2026-04-12', 29920, 500.00, 14960000.00),
    (501, 1, 1, '2026-05-05', 30000, 90.00, 2700000.00);

-- Партнер 2: объем доводим до 320 000 шт. (скидка 15%)
INSERT INTO sales (sale_id, partner_id, product_id, sale_date, quantity, unit_price, total_amount)
VALUES
    (502, 2, 2, '2026-04-20', 180000, 500.00, 90000000.00),
    (503, 2, 4, '2026-06-11', 139800, 350.00, 48930000.00);

-- Партнер 3: объем доводим до 30 000 шт. (скидка 5%)
INSERT INTO sales (sale_id, partner_id, product_id, sale_date, quantity, unit_price, total_amount)
VALUES
    (504, 3, 1, '2026-03-30', 14850, 90.00, 1336500.00),
    (505, 3, 2, '2026-07-01', 15000, 500.00, 7500000.00);

-- Сброс последовательностей после вставки с явными id
SELECT setval('partners_partner_id_seq', (SELECT COALESCE(MAX(partner_id), 0) FROM partners));
SELECT setval('sales_sale_id_seq', (SELECT COALESCE(MAX(sale_id), 0) FROM sales));