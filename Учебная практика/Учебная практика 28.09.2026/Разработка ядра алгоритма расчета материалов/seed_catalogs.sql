INSERT INTO product_types (product_type_id, type_name, coefficient) VALUES
    (1, 'Тип продукции 1', 1.00),
    (2, 'Тип продукции 2', 1.50);

INSERT INTO material_types (material_type_id, type_name, defect_percent) VALUES
    (1, 'Материал 1', 0.00),
    (2, 'Материал 2', 5.00);

SELECT setval('product_types_product_type_id_seq', 2);
SELECT setval('material_types_material_type_id_seq', 2);
