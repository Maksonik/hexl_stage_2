from unittest.mock import MagicMock, patch

import pytest

from partner_sales import (
    create_connection,
    fetch_partner_sales_total,
    get_partner_with_discount,
)


def test_fetch_partner_sales_total_returns_dict() -> None:
    cursor = MagicMock()
    cursor.fetchone.return_value = (
        1,
        "ООО Альфа",
        "адрес",
        "7701234567",
        "Иванов",
        "+7900",
        "a@a.ru",
        5,
        10500,
    )
    cursor.description = [
        MagicMock(name="partner_id"),
        MagicMock(name="name"),
        MagicMock(name="legal_address"),
        MagicMock(name="inn"),
        MagicMock(name="director_name"),
        MagicMock(name="phone"),
        MagicMock(name="email"),
        MagicMock(name="rating"),
        MagicMock(name="total_quantity"),
    ]
    for mock_column, column_name in zip(
        cursor.description,
        [
            "partner_id",
            "name",
            "legal_address",
            "inn",
            "director_name",
            "phone",
            "email",
            "rating",
            "total_quantity",
        ],
    ):
        mock_column.name = column_name
    connection = MagicMock()
    connection.cursor.return_value.__enter__.return_value = cursor
    result = fetch_partner_sales_total(connection, 1)
    assert result is not None
    assert result["partner_id"] == 1
    assert result["total_quantity"] == 10500
    cursor.execute.assert_called_once()


def test_fetch_partner_sales_total_not_found() -> None:
    cursor = MagicMock()
    cursor.fetchone.return_value = None
    connection = MagicMock()
    connection.cursor.return_value.__enter__.return_value = cursor
    assert fetch_partner_sales_total(connection, 999) is None


def test_get_partner_with_discount_uses_injected_connection() -> None:
    connection = MagicMock()
    partner_row = {
        "partner_id": 1,
        "name": "ООО Альфа",
        "legal_address": "адрес",
        "inn": "7701234567",
        "director_name": "Иванов",
        "phone": "+7900",
        "email": "a@a.ru",
        "rating": 5,
        "total_quantity": 10500,
    }
    with patch(
        "partner_sales.fetch_partner_sales_total",
        return_value=partner_row,
    ) as fetch_mock:
        result = get_partner_with_discount(1, connection=connection)
    fetch_mock.assert_called_once_with(connection, 1)
    assert result is not None
    assert result["discount_percent"] == 5
    assert result["total_quantity"] == 10500
    connection.close.assert_not_called()


def test_get_partner_with_discount_not_found() -> None:
    connection = MagicMock()
    with patch("partner_sales.fetch_partner_sales_total", return_value=None):
        assert get_partner_with_discount(999, connection=connection) is None


def test_get_partner_with_discount_opens_and_closes_connection() -> None:
    connection = MagicMock()
    partner_row = {
        "partner_id": 2,
        "name": "ООО Бета",
        "legal_address": "адрес",
        "inn": "1601234567",
        "director_name": "Петров",
        "phone": "+7901",
        "email": "b@b.ru",
        "rating": 3,
        "total_quantity": 55000,
    }
    with patch("partner_sales.create_connection", return_value=connection):
        with patch(
            "partner_sales.fetch_partner_sales_total",
            return_value=partner_row,
        ):
            result = get_partner_with_discount(2)
    assert result is not None
    assert result["discount_percent"] == 10
    connection.close.assert_called_once()


def test_create_connection_uses_env_defaults() -> None:
    with patch("partner_sales.psycopg2.connect") as connect_mock:
        connect_mock.return_value = MagicMock()
        create_connection()
    connect_mock.assert_called_once_with(
        host="localhost",
        port="5432",
        dbname="partners",
        user="partners",
        password="partners",
    )


@pytest.mark.parametrize(
    ("total_quantity", "expected_discount"),
    [
        (0, 0),
        (9999, 0),
        (10000, 5),
        (55000, 10),
        (300000, 15),
    ],
)
def test_get_partner_with_discount_levels(
    total_quantity: int,
    expected_discount: int,
) -> None:
    connection = MagicMock()
    partner_row = {
        "partner_id": 3,
        "name": "ООО Гамма",
        "legal_address": "адрес",
        "inn": "6301234567",
        "director_name": "Сидоров",
        "phone": "+7902",
        "email": "c@c.ru",
        "rating": 1,
        "total_quantity": total_quantity,
    }
    with patch(
        "partner_sales.fetch_partner_sales_total",
        return_value=partner_row,
    ):
        result = get_partner_with_discount(3, connection=connection)
    assert result is not None
    assert result["discount_percent"] == expected_discount
