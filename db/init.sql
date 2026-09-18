CREATE TABLE partner_types (
    partner_type_id SERIAL PRIMARY KEY,
    name            VARCHAR(100) NOT NULL UNIQUE
);

CREATE TABLE partners (
    partner_id      SERIAL PRIMARY KEY,
    partner_type_id INTEGER      NOT NULL,
    name            VARCHAR(255) NOT NULL,
    legal_address   VARCHAR(500) NOT NULL,
    inn             VARCHAR(12)  NOT NULL UNIQUE,
    director_name   VARCHAR(255) NOT NULL,
    phone           VARCHAR(20)  NOT NULL,
    email           VARCHAR(255) NOT NULL UNIQUE,
    rating          INTEGER      NOT NULL DEFAULT 0,
    CONSTRAINT fk_partners_partner_type
        FOREIGN KEY (partner_type_id) REFERENCES partner_types (partner_type_id),
    CONSTRAINT chk_partners_rating CHECK (rating >= 0)
);

CREATE TABLE products (
    product_id SERIAL PRIMARY KEY,
    name       VARCHAR(255)   NOT NULL,
    article    VARCHAR(50)    NOT NULL UNIQUE,
    unit_price NUMERIC(12, 2) NOT NULL,
    CONSTRAINT chk_products_unit_price CHECK (unit_price >= 0)
);

CREATE TABLE sales_history (
    sale_id     SERIAL PRIMARY KEY,
    partner_id  INTEGER        NOT NULL,
    product_id  INTEGER        NOT NULL,
    quantity    INTEGER        NOT NULL,
    sale_date   DATE           NOT NULL,
    unit_price  NUMERIC(12, 2) NOT NULL,
    CONSTRAINT fk_sales_history_partner
        FOREIGN KEY (partner_id) REFERENCES partners (partner_id),
    CONSTRAINT fk_sales_history_product
        FOREIGN KEY (product_id) REFERENCES products (product_id),
    CONSTRAINT chk_sales_history_quantity CHECK (quantity > 0),
    CONSTRAINT chk_sales_history_unit_price CHECK (unit_price >= 0)
);

CREATE INDEX idx_sales_history_partner_id ON sales_history (partner_id);
CREATE INDEX idx_sales_history_product_id ON sales_history (product_id);
CREATE INDEX idx_sales_history_sale_date ON sales_history (sale_date);

INSERT INTO partner_types (name) VALUES
    ('Розница'),
    ('Опт');

INSERT INTO partners (
    partner_type_id,
    name,
    legal_address,
    inn,
    director_name,
    phone,
    email,
    rating
) VALUES
    (1, 'ООО Альфа', 'г. Москва, ул. Ленина, 1', '7701234567', 'Иванов И.И.', '+79001112233', 'alpha@example.com', 5),
    (2, 'ООО Бета', 'г. Казань, ул. Баумана, 10', '1601234567', 'Петров П.П.', '+79004445566', 'beta@example.com', 3),
    (1, 'ООО Гамма', 'г. Самара, ул. Победы, 5', '6301234567', 'Сидоров С.С.', '+79007778899', 'gamma@example.com', 1);

INSERT INTO products (name, article, unit_price) VALUES
    ('Доска паркетная', 'PRK-001', 1500.00),
    ('Ламинат дуб', 'LAM-010', 900.00),
    ('Плинтус', 'PLN-003', 250.00);

INSERT INTO sales_history (partner_id, product_id, quantity, sale_date, unit_price) VALUES
    (1, 1, 8000, '2025-01-10', 1500.00),
    (1, 2, 2500, '2025-02-15', 900.00),
    (2, 1, 40000, '2025-03-01', 1450.00),
    (2, 3, 15000, '2025-03-20', 240.00);
