SELECT 'partners' AS table_name, COUNT(*) AS row_count FROM partners
UNION ALL SELECT 'products', COUNT(*) FROM products
UNION ALL SELECT 'sales', COUNT(*) FROM sales;

SELECT p.company_name, COALESCE(SUM(s.quantity), 0) AS total_quantity
FROM partners p
LEFT JOIN sales s ON s.partner_id = p.partner_id
GROUP BY p.partner_id
ORDER BY p.company_name;
