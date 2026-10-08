"""ETL: чтение сырых CSV заказчика, очистка и загрузка в PostgreSQL."""
import csv
import io
import re
import sys
from datetime import date
from decimal import Decimal
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent
CORE = DATA_DIR.parent / "Реализация ядра бизнес-логики (Расчеты и алгоритмы)"
sys.path.insert(0, str(CORE))

import db

PARTNER_TYPES = ("ООО", "АО", "ЗАО", "ИП")


def read_csv(path):
    raw = path.read_bytes()
    try:
        text = raw.decode("utf-8-sig")
    except UnicodeDecodeError:
        # products_raw.csv выгружен в Windows-1251, остальные файлы — в UTF-8.
        text = raw.decode("cp1251")
    return list(csv.DictReader(io.StringIO(text, newline="")))


def clean_text(value):
    """TRIM по краям и один пробел вместо нескольких внутри строки."""
    return " ".join(value.split())


def partner_type(partner_name):
    # Типа партнёра в файле нет — берём организационную форму из начала названия.
    first_word = partner_name.split(" ", 1)[0]
    return first_word if first_word in PARTNER_TYPES else "Другое"


def normalize_date(value):
    """Приводит ДД.ММ.ГГГГ и ГГГГ.ММ.ДД (разделители . / -) к дате ГГГГ-ММ-ДД."""
    first, month, last = re.split(r"[./-]", value.strip())
    if len(first) == 4:
        return date(int(first), int(month), int(last))
    return date(int(last), int(month), int(first))


def clean_partners(rows):
    partners = []
    for row in rows:
        partner_name = clean_text(row["partner_name"])
        partners.append({
            "partner_id": int(row["partner_id"]),
            "partner_name": partner_name,
            "partner_type": partner_type(partner_name),
            "inn": clean_text(row["inn"]),
            "email": clean_text(row["email"]),
        })
    return partners


def clean_products(rows):
    return [
        {
            "product_id": int(row["product_id"]),
            "product_name": clean_text(row["product_name"]),
            "price": Decimal(row["price"].strip()),
        }
        for row in rows
    ]


def clean_sales(rows, partner_ids):
    """Возвращает чистые продажи и ID продаж, у которых нет партнёра в partners."""
    sales = []
    rejected = []
    for row in rows:
        if int(row["partner_id"]) not in partner_ids:
            rejected.append(int(row["sale_id"]))
            continue
        sales.append({
            "sale_id": int(row["sale_id"]),
            "partner_id": int(row["partner_id"]),
            "product_id": int(row["product_id"]),
            "sale_date": normalize_date(row["sale_date"]),
            "quantity": int(row["quantity"]),
            "amount": Decimal(row["amount"].strip()),
        })
    return sales, rejected


def extract_and_clean(data_dir=DATA_DIR):
    partners = clean_partners(read_csv(data_dir / "partners_raw.csv"))
    products = clean_products(read_csv(data_dir / "products_raw.csv"))
    partner_ids = {partner["partner_id"] for partner in partners}
    sales, rejected = clean_sales(read_csv(data_dir / "sales_history_raw.csv"), partner_ids)
    return partners, products, sales, rejected


def load(conn, partners, products, sales):
    with conn.cursor() as cursor:
        cursor.executemany(
            """INSERT INTO partners (partner_id, partner_name, partner_type, inn, email)
               VALUES (%(partner_id)s, %(partner_name)s, %(partner_type)s, %(inn)s, %(email)s)""",
            partners,
        )
        cursor.executemany(
            "INSERT INTO products (product_id, product_name, price) VALUES (%(product_id)s, %(product_name)s, %(price)s)",
            products,
        )
        cursor.executemany(
            """INSERT INTO sales_history (sale_id, partner_id, product_id, sale_date, quantity, amount)
               VALUES (%(sale_id)s, %(partner_id)s, %(product_id)s, %(sale_date)s, %(quantity)s, %(amount)s)""",
            sales,
        )
        # ID партнёров пришли из файла, поэтому сдвигаем счётчик SERIAL за максимальный ID.
        cursor.execute("SELECT setval('partners_partner_id_seq', (SELECT MAX(partner_id) FROM partners))")


def main():
    partners, products, sales, rejected = extract_and_clean()
    conn = db.connect()
    try:
        load(conn, partners, products, sales)
        conn.commit()
    finally:
        conn.close()

    print(f"partners: {len(partners)}, products: {len(products)}, sales_history: {len(sales)}")
    print(f"Отброшены продажи с несуществующим партнёром: {rejected}")


if __name__ == "__main__":
    main()
