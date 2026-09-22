-- Суммарный объем продаж по всем партнерам (SUM(quantity) + LEFT JOIN).
-- Партнеры без истории продаж тоже попадают в выборку (total_quantity = 0).

SELECT
    p.partner_id,
    p.company_name,
    p.inn,
    p.contact_email,
    p.phone,
    p.rating,
    COALESCE(SUM(s.quantity), 0) AS total_quantity
FROM partners p
LEFT JOIN sales s ON s.partner_id = p.partner_id
GROUP BY
    p.partner_id,
    p.company_name,
    p.inn,
    p.contact_email,
    p.phone,
    p.rating
ORDER BY p.company_name;

-- Суммарный объем продаж по конкретному партнеру (partner_id = 1).
-- При отсутствии истории вернет total_quantity = 0.

SELECT
    p.partner_id,
    p.company_name,
    COALESCE(SUM(s.quantity), 0) AS total_quantity
FROM partners p
LEFT JOIN sales s ON s.partner_id = p.partner_id
WHERE p.partner_id = 1
GROUP BY
    p.partner_id,
    p.company_name;