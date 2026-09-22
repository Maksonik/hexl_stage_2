-- 1. Удаление таблиц (если существуют)
DROP TABLE IF EXISTS sales CASCADE;
DROP TABLE IF EXISTS products CASCADE;
DROP TABLE IF EXISTS partners CASCADE;

-- 2. Создание таблицы partners
CREATE TABLE partners (
    partner_id      SERIAL PRIMARY KEY,
    company_name    VARCHAR(255) NOT NULL,
    inn             VARCHAR(12) NOT NULL UNIQUE,
    contact_email   VARCHAR(255) NOT NULL UNIQUE,
    phone           VARCHAR(50),
    rating          DECIMAL(3,2) CHECK (rating >= 0 AND rating <= 5),
    created_at      TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- 3. Создание таблицы products
CREATE TABLE products (
    product_id      SERIAL PRIMARY KEY,
    product_name    VARCHAR(255) NOT NULL UNIQUE,
    unit            VARCHAR(50) NOT NULL DEFAULT 'шт.',
    base_price      DECIMAL(12,2) NOT NULL CHECK (base_price >= 0)
);

-- 4. Создание таблицы sales
CREATE TABLE sales (
    sale_id         SERIAL PRIMARY KEY,
    partner_id      INT NOT NULL REFERENCES partners(partner_id) ON DELETE RESTRICT,
    product_id      INT NOT NULL REFERENCES products(product_id) ON DELETE RESTRICT,
    sale_date       DATE NOT NULL,
    quantity        INT NOT NULL CHECK (quantity > 0),
    unit_price      DECIMAL(12,2) NOT NULL CHECK (unit_price >= 0),
    total_amount    DECIMAL(12,2) NOT NULL CHECK (total_amount >= 0),
    created_at      TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT chk_total_amount CHECK (ABS(total_amount - quantity * unit_price) < 0.005 * quantity)
);

