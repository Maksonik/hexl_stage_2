SELECT 'partners' AS table_name, COUNT(*) AS row_count FROM partners
UNION ALL SELECT 'products', COUNT(*) FROM products
UNION ALL SELECT 'sales_history', COUNT(*) FROM sales_history;

SELECT partner_id, partner_name, partner_type, inn, email
FROM partners
ORDER BY partner_id;

SELECT s.sale_id, p.partner_name, pr.product_name, s.sale_date, s.quantity, s.amount
FROM sales_history s
JOIN partners p ON p.partner_id = s.partner_id
JOIN products pr ON pr.product_id = s.product_id
ORDER BY s.sale_id;
