INSERT INTO product_types (product_type_id, type_name, coefficient) VALUES
    (1, 'Тип продукции 1', 1.00),
    (2, 'Тип продукции 2', 1.50)
ON CONFLICT (product_type_id) DO NOTHING;

INSERT INTO material_types (material_type_id, type_name, defect_percent) VALUES
    (1, 'Материал 1', 0.00),
    (2, 'Материал 2', 5.00)
ON CONFLICT (material_type_id) DO NOTHING;

SELECT setval('product_types_product_type_id_seq', (SELECT MAX(product_type_id) FROM product_types));
SELECT setval('material_types_material_type_id_seq', (SELECT MAX(material_type_id) FROM material_types));
