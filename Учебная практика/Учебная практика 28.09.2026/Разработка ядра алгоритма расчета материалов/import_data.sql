\set ON_ERROR_STOP on

\copy partners (partner_id, company_name, inn, contact_email, phone, rating, partner_type, address, director_name) FROM 'import_partners_clean.csv' WITH (FORMAT csv, HEADER true, DELIMITER ',', ENCODING 'UTF8', NULL '');

SELECT setval('partners_partner_id_seq', (SELECT COALESCE(MAX(partner_id), 1) FROM partners));

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

INSERT INTO products (product_name, unit, base_price)
SELECT DISTINCT product_name, 'шт.', total_amount / quantity
FROM tmp_sales_raw
ON CONFLICT (product_name) DO NOTHING;

INSERT INTO sales (sale_id, partner_id, product_id, sale_date, quantity, unit_price, total_amount)
SELECT s.sale_id, s.partner_id, p.product_id, s.sale_date, s.quantity,
       s.total_amount / s.quantity, s.total_amount
FROM tmp_sales_raw s
JOIN products p ON p.product_name = s.product_name
WHERE EXISTS (SELECT 1 FROM partners x WHERE x.partner_id = s.partner_id);

DROP TABLE tmp_sales_raw;

SELECT setval('sales_sale_id_seq', (SELECT COALESCE(MAX(sale_id), 1) FROM sales));

SELECT 'partners' AS table_name, COUNT(*) AS row_count FROM partners
UNION ALL SELECT 'products', COUNT(*) FROM products
UNION ALL SELECT 'sales', COUNT(*) FROM sales;
