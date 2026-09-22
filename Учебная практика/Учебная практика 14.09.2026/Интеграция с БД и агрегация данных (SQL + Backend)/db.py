"""Подключение к БД и агрегация объема продаж по партнерам."""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "Разработка ядра бизнес-логики (Расчет скидки)"))

import psycopg2
import psycopg2.extras

from discount import calculate_partner_discount

DSN = os.environ.get("PRACTICE_DB_DSN", "dbname=practice_db")

SUMMARY_QUERY = """
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
    ORDER BY p.company_name
"""

SUMMARY_ONE_QUERY = """
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
    WHERE p.partner_id = %s
    GROUP BY
        p.partner_id,
        p.company_name,
        p.inn,
        p.contact_email,
        p.phone,
        p.rating
    ORDER BY p.company_name
"""


def connect():
    return psycopg2.connect(DSN)


def get_partner_total_quantity(conn, partner_id):
    """Суммарный объем продаж по конкретному партнеру."""
    with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
        cur.execute(SUMMARY_ONE_QUERY, (partner_id,))
        return cur.fetchone()


def get_partner_sales_summary(conn):
    """Список партнеров с суммарным объемом продаж."""
    with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
        cur.execute(SUMMARY_QUERY)
        return cur.fetchall()


def _partner_dict(row):
    total_quantity = row["total_quantity"]
    return {
        "partner_id": row["partner_id"],
        "company_name": row["company_name"],
        "inn": row["inn"],
        "contact_email": row["contact_email"],
        "phone": row["phone"],
        "rating": float(row["rating"]) if row["rating"] is not None else None,
        "total_quantity": total_quantity,
        "discount_percent": calculate_partner_discount(total_quantity),
    }


def get_partners_with_discount(conn):
    """Список партнеров, дополненный текущим процентом скидки."""
    return [_partner_dict(row) for row in get_partner_sales_summary(conn)]


def get_partner_with_discount(conn, partner_id):
    """Данные партнера, дополненные текущим процентом скидки."""
    row = get_partner_total_quantity(conn, partner_id)
    if row is None:
        return None
    return _partner_dict(row)