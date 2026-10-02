-- Дополнительные продажи для демонстрации порогов скидки.
INSERT INTO partners (partner_id, company_name, partner_type, inn, contact_email, phone, rating, address, director_name)
VALUES (5, 'ООО "Партнер без истории"', 'ООО', '7702000005', 'no_history@example.com', '+7 (900) 111-22-33', 4, '', '');

INSERT INTO products (product_name, unit, base_price)
VALUES ('Средство для уборки', 'шт.', 350.00)
ON CONFLICT (product_name) DO NOTHING;

INSERT INTO sales (sale_id, partner_id, product_id, sale_date, quantity, unit_price, total_amount)
VALUES
    (500, 1, (SELECT product_id FROM products WHERE product_name = 'Мыло жидкое "Стандарт"'), '2026-04-12', 29920, 500.00, 14960000.00),
    (501, 1, (SELECT product_id FROM products WHERE product_name = 'Стиральный порошок "Альфа"'), '2026-05-05', 30000, 90.00, 2700000.00),
    (502, 2, (SELECT product_id FROM products WHERE product_name = 'Мыло жидкое "Стандарт"'), '2026-04-20', 180000, 500.00, 90000000.00),
    (503, 2, (SELECT product_id FROM products WHERE product_name = 'Средство для уборки'), '2026-06-11', 139800, 350.00, 48930000.00),
    (504, 3, (SELECT product_id FROM products WHERE product_name = 'Стиральный порошок "Альфа"'), '2026-03-30', 14850, 90.00, 1336500.00),
    (505, 3, (SELECT product_id FROM products WHERE product_name = 'Мыло жидкое "Стандарт"'), '2026-07-01', 15000, 500.00, 7500000.00);

SELECT setval('partners_partner_id_seq', (SELECT COALESCE(MAX(partner_id), 1) FROM partners));
SELECT setval('sales_sale_id_seq', (SELECT COALESCE(MAX(sale_id), 1) FROM sales));
