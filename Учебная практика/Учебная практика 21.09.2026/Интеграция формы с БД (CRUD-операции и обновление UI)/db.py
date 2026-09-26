"""Подключение к БД и работа с партнёрами."""
import os

import psycopg2
import psycopg2.extras

from discount import calculate_partner_discount

DSN = os.environ.get("PRACTICE_DB_DSN", "dbname=practice_db_2109")

SUMMARY_QUERY = """
    SELECT p.partner_id, p.company_name, p.partner_type, p.inn,
           p.contact_email, p.phone, p.rating, p.address, p.director_name,
           COALESCE(SUM(s.quantity), 0) AS total_quantity
    FROM partners p
    LEFT JOIN sales s ON s.partner_id = p.partner_id
    GROUP BY p.partner_id
    ORDER BY p.company_name
"""

ONE_QUERY = """
    SELECT p.partner_id, p.company_name, p.partner_type, p.inn,
           p.contact_email, p.phone, p.rating, p.address, p.director_name,
           COALESCE(SUM(s.quantity), 0) AS total_quantity
    FROM partners p
    LEFT JOIN sales s ON s.partner_id = p.partner_id
    WHERE p.partner_id = %s
    GROUP BY p.partner_id
"""


def connect():
    return psycopg2.connect(DSN)


def _partner_dict(row):
    return {
        "partner_id": row["partner_id"],
        "company_name": row["company_name"],
        "partner_type": row["partner_type"],
        "inn": row["inn"],
        "contact_email": row["contact_email"],
        "phone": row["phone"] or "",
        "rating": row["rating"],
        "address": row["address"] or "",
        "director_name": row["director_name"] or "",
        "total_quantity": row["total_quantity"],
        "discount_percent": calculate_partner_discount(row["total_quantity"]),
    }


def get_partner_sales_summary(conn):
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
        data["company_name"],
        data["partner_type"],
        data["inn"],
        data["contact_email"],
        data["phone"] or None,
        data["rating"],
        data["address"] or None,
        data["director_name"] or None,
    )


def create_partner(conn, data):
    with conn.cursor() as cursor:
        cursor.execute(
            """INSERT INTO partners
               (company_name, partner_type, inn, contact_email, phone, rating, address, director_name)
               VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
               RETURNING partner_id""",
            _values(data),
        )
        return cursor.fetchone()[0]


def update_partner(conn, partner_id, data):
    with conn.cursor() as cursor:
        cursor.execute(
            """UPDATE partners
               SET company_name = %s, partner_type = %s, inn = %s, contact_email = %s,
                   phone = %s, rating = %s, address = %s, director_name = %s
               WHERE partner_id = %s""",
            (*_values(data), partner_id),
        )
        return cursor.rowcount == 1

