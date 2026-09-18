import os

import psycopg2
from psycopg2.extensions import connection as PgConnection

from partner_discount import calculate_partner_discount


PARTNER_SALES_SQL = """
SELECT
    p.partner_id,
    p.name,
    p.legal_address,
    p.inn,
    p.director_name,
    p.phone,
    p.email,
    p.rating,
    COALESCE(SUM(s.quantity), 0) AS total_quantity
FROM partners AS p
LEFT JOIN sales_history AS s ON s.partner_id = p.partner_id
WHERE p.partner_id = %s
GROUP BY
    p.partner_id,
    p.name,
    p.legal_address,
    p.inn,
    p.director_name,
    p.phone,
    p.email,
    p.rating
"""

PARTNERS_LIST_SQL = """
SELECT
    p.partner_id,
    pt.name AS partner_type,
    p.name,
    p.director_name,
    p.phone,
    p.rating,
    COALESCE(SUM(s.quantity), 0) AS total_quantity
FROM partners AS p
LEFT JOIN partner_types AS pt ON pt.partner_type_id = p.partner_type_id
LEFT JOIN sales_history AS s ON s.partner_id = p.partner_id
GROUP BY
    p.partner_id,
    pt.name,
    p.name,
    p.director_name,
    p.phone,
    p.rating
ORDER BY p.partner_id
"""


def create_connection() -> PgConnection:
    return psycopg2.connect(
        host=os.getenv("POSTGRES_HOST", "localhost"),
        port=os.getenv("POSTGRES_PORT", "5432"),
        dbname=os.getenv("POSTGRES_DB", "partners"),
        user=os.getenv("POSTGRES_USER", "partners"),
        password=os.getenv("POSTGRES_PASSWORD", "partners"),
    )


def apply_discount(partner: dict) -> dict:
    total_quantity = int(partner.get("total_quantity") or 0)
    partner["total_quantity"] = total_quantity
    partner["discount_percent"] = calculate_partner_discount(total_quantity)
    return partner


def fetch_partner_sales_total(
    connection: PgConnection,
    partner_id: int,
) -> dict | None:
    with connection.cursor() as cursor:
        cursor.execute(PARTNER_SALES_SQL, (partner_id,))
        row = cursor.fetchone()
        if row is None:
            return None
        columns = [column.name for column in cursor.description]
        return dict(zip(columns, row))


def fetch_partners_list(connection: PgConnection) -> list[dict]:
    with connection.cursor() as cursor:
        cursor.execute(PARTNERS_LIST_SQL)
        rows = cursor.fetchall()
        columns = [column.name for column in cursor.description]
        return [dict(zip(columns, row)) for row in rows]


def get_partner_with_discount(
    partner_id: int,
    connection: PgConnection | None = None,
) -> dict | None:
    owns_connection = connection is None
    if owns_connection:
        connection = create_connection()
    try:
        partner = fetch_partner_sales_total(connection, partner_id)
        if partner is None:
            return None
        return apply_discount(partner)
    finally:
        if owns_connection:
            connection.close()


def list_partners_with_discount(
    connection: PgConnection | None = None,
) -> list[dict]:
    owns_connection = connection is None
    if owns_connection:
        connection = create_connection()
    try:
        partners = fetch_partners_list(connection)
        return [apply_discount(partner) for partner in partners]
    finally:
        if owns_connection:
            connection.close()
