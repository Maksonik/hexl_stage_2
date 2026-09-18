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


def create_connection() -> PgConnection:
    return psycopg2.connect(
        host=os.getenv("POSTGRES_HOST", "localhost"),
        port=os.getenv("POSTGRES_PORT", "5432"),
        dbname=os.getenv("POSTGRES_DB", "partners"),
        user=os.getenv("POSTGRES_USER", "partners"),
        password=os.getenv("POSTGRES_PASSWORD", "partners"),
    )


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
        total_quantity = int(partner["total_quantity"])
        partner["total_quantity"] = total_quantity
        partner["discount_percent"] = calculate_partner_discount(total_quantity)
        return partner
    finally:
        if owns_connection:
            connection.close()
