DROP TABLE IF EXISTS sales CASCADE;
DROP TABLE IF EXISTS products CASCADE;
DROP TABLE IF EXISTS partners CASCADE;

CREATE TABLE partners (
    partner_id      SERIAL PRIMARY KEY,
    company_name    VARCHAR(255) NOT NULL,
    partner_type    VARCHAR(20) NOT NULL CHECK (partner_type IN ('ООО', 'ЗАО', 'ИП', 'ТК', 'Другое')),
    inn             VARCHAR(12) NOT NULL UNIQUE,
    contact_email   VARCHAR(255) NOT NULL UNIQUE,
    phone           VARCHAR(50),
    rating          INTEGER NOT NULL DEFAULT 0 CHECK (rating >= 0),
    address         TEXT,
    director_name   VARCHAR(255),
    created_at      TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE products (
    product_id      SERIAL PRIMARY KEY,
    product_name    VARCHAR(255) NOT NULL UNIQUE,
    unit            VARCHAR(50) NOT NULL DEFAULT 'шт.',
    base_price      DECIMAL(12,2) NOT NULL CHECK (base_price >= 0)
);

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
