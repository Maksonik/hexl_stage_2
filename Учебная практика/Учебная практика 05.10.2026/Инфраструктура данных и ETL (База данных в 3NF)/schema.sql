DROP TABLE IF EXISTS sales_history CASCADE;
DROP TABLE IF EXISTS products CASCADE;
DROP TABLE IF EXISTS partners CASCADE;
DROP TABLE IF EXISTS product_types CASCADE;
DROP TABLE IF EXISTS material_types CASCADE;

CREATE TABLE partners (
    partner_id      SERIAL PRIMARY KEY,
    partner_name    VARCHAR(255) NOT NULL,
    partner_type    VARCHAR(20) NOT NULL CHECK (partner_type IN ('ООО', 'АО', 'ЗАО', 'ИП', 'Другое')),
    rating          INT NOT NULL DEFAULT 0 CHECK (rating >= 0),
    inn             VARCHAR(12) NOT NULL UNIQUE,
    email           VARCHAR(255) NOT NULL UNIQUE,
    address         TEXT,
    director_name   VARCHAR(255),
    phone           VARCHAR(50)
);

CREATE TABLE products (
    product_id      SERIAL PRIMARY KEY,
    product_name    VARCHAR(255) NOT NULL UNIQUE,
    price           DECIMAL(12,2) NOT NULL CHECK (price >= 0)
);

CREATE TABLE sales_history (
    sale_id         SERIAL PRIMARY KEY,
    partner_id      INT NOT NULL REFERENCES partners(partner_id) ON DELETE RESTRICT,
    product_id      INT NOT NULL REFERENCES products(product_id) ON DELETE RESTRICT,
    sale_date       DATE NOT NULL,
    quantity        INT NOT NULL CHECK (quantity > 0),
    amount          DECIMAL(12,2) NOT NULL CHECK (amount >= 0)
);

CREATE TABLE product_types (
    product_type_id SERIAL PRIMARY KEY,
    type_name       VARCHAR(100) NOT NULL UNIQUE,
    coefficient     DECIMAL(10,2) NOT NULL CHECK (coefficient > 0)
);

CREATE TABLE material_types (
    material_type_id SERIAL PRIMARY KEY,
    type_name        VARCHAR(100) NOT NULL UNIQUE,
    defect_percent   DECIMAL(5,2) NOT NULL CHECK (defect_percent >= 0)
);
