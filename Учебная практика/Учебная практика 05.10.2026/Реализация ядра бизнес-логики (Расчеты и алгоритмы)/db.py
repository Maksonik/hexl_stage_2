"""Подключение к БД и запросы приложения."""
import os
from pathlib import Path

import psycopg2
import psycopg2.extras

DB_NAME = "practice_db_0510"
SOCKET_DIRS = ("/var/run/postgresql", "/tmp")

SUMMARY_QUERY = """
    SELECT p.partner_id, p.partner_name, p.partner_type, p.rating, p.inn,
           p.address, p.director_name, p.phone, p.email,
           COALESCE(SUM(s.quantity), 0) AS total_quantity
    FROM partners p
    LEFT JOIN sales_history s ON s.partner_id = p.partner_id
    GROUP BY p.partner_id
    ORDER BY p.partner_name
"""

ONE_QUERY = """
    SELECT p.partner_id, p.partner_name, p.partner_type, p.rating, p.inn,
           p.address, p.director_name, p.phone, p.email,
           COALESCE(SUM(s.quantity), 0) AS total_quantity
    FROM partners p
    LEFT JOIN sales_history s ON s.partner_id = p.partner_id
    WHERE p.partner_id = %s
    GROUP BY p.partner_id
"""


def default_dsn():
    """Параметры подключения к локальному серверу, если PRACTICE_DB_DSN не задан."""
    dsn = f"dbname={DB_NAME}"
    if any(os.environ.get(name) for name in ("PGHOST", "PGPORT", "PGSERVICE")):
        return dsn
    # В Debian/Ubuntu кластер может слушать не 5432: psql узнаёт порт сам,
    # а libpq из psycopg2 — нет, поэтому берём порт из имени файла сокета.
    for directory in SOCKET_DIRS:
        ports = sorted(
            int(path.suffix[1:])
            for path in Path(directory).glob(".s.PGSQL.*")
            if path.suffix[1:].isdigit()
        )
        if ports:
            port = 5432 if 5432 in ports else ports[0]
            return f"{dsn} host={directory} port={port}"
    return dsn


def connect():
    return psycopg2.connect(os.environ.get("PRACTICE_DB_DSN") or default_dsn())


def _partner_dict(row):
    partner = dict(row)
    for key in ("address", "director_name", "phone"):
        partner[key] = partner[key] or ""
    partner["total_quantity"] = int(partner["total_quantity"])
    return partner


def get_partners(conn):
    with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
        cursor.execute(SUMMARY_QUERY)
        return [_partner_dict(row) for row in cursor.fetchall()]


def get_partner(conn, partner_id):
    with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
        cursor.execute(ONE_QUERY, (partner_id,))
        row = cursor.fetchone()
        return _partner_dict(row) if row else None


def _values(data):
    return (
        data["partner_name"],
        data["partner_type"],
        data["rating"],
        data["inn"],
        data["address"] or None,
        data["director_name"] or None,
        data["phone"] or None,
        data["email"],
    )


def create_partner(conn, data):
    with conn.cursor() as cursor:
        cursor.execute(
            """INSERT INTO partners
               (partner_name, partner_type, rating, inn, address, director_name, phone, email)
               VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
               RETURNING partner_id""",
            _values(data),
        )
        return cursor.fetchone()[0]


def update_partner(conn, partner_id, data):
    with conn.cursor() as cursor:
        cursor.execute(
            """UPDATE partners
               SET partner_name = %s, partner_type = %s, rating = %s, inn = %s,
                   address = %s, director_name = %s, phone = %s, email = %s
               WHERE partner_id = %s""",
            (*_values(data), partner_id),
        )
        return cursor.rowcount == 1


def get_partner_sales(conn, partner_id):
    with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
        cursor.execute(
            """SELECT p.product_name, s.sale_date, s.quantity
               FROM sales_history s
               JOIN products p ON p.product_id = s.product_id
               WHERE s.partner_id = %s
               ORDER BY s.sale_date DESC, s.sale_id DESC""",
            (partner_id,),
        )
        return [
            {
                "product_name": row["product_name"],
                "sale_date": row["sale_date"].isoformat(),
                "quantity": row["quantity"],
            }
            for row in cursor.fetchall()
        ]


def get_material_factors(product_type_id, material_type_id):
    conn = connect()
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT coefficient FROM product_types WHERE product_type_id = %s",
                (product_type_id,),
            )
            product = cursor.fetchone()
            cursor.execute(
                "SELECT defect_percent FROM material_types WHERE material_type_id = %s",
                (material_type_id,),
            )
            material = cursor.fetchone()
        if product is None or material is None:
            return None
        return product[0], material[0]
    finally:
        conn.close()
