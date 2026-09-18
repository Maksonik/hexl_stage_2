from unittest.mock import patch

from app import app, main


def test_index_returns_html() -> None:
    client = app.test_client()
    response = client.get("/")
    assert response.status_code == 200
    assert b"CRM: " in response.data or "CRM".encode() in response.data
    assert b"partners" in response.data


def test_api_partners_success() -> None:
    partners = [
        {
            "partner_id": 1,
            "partner_type": "Розница",
            "name": "ООО Альфа",
            "director_name": "Иванов И.И.",
            "phone": "+79001112233",
            "rating": 5,
            "total_quantity": 10500,
            "discount_percent": 5,
        },
        {
            "partner_id": 3,
            "partner_type": "Розница",
            "name": "ООО Гамма",
            "director_name": "Сидоров С.С.",
            "phone": "+79007778899",
            "rating": 1,
            "total_quantity": 0,
            "discount_percent": 0,
        },
    ]
    client = app.test_client()
    with patch("app.list_partners_with_discount", return_value=partners):
        response = client.get("/api/partners")
    assert response.status_code == 200
    payload = response.get_json()
    assert len(payload) == 2
    assert payload[1]["discount_percent"] == 0


def test_api_partners_empty_list() -> None:
    client = app.test_client()
    with patch("app.list_partners_with_discount", return_value=[]):
        response = client.get("/api/partners")
    assert response.status_code == 200
    assert response.get_json() == []


def test_api_partners_db_error() -> None:
    client = app.test_client()
    with patch(
        "app.list_partners_with_discount",
        side_effect=RuntimeError("db unavailable"),
    ):
        response = client.get("/api/partners")
    assert response.status_code == 500
    payload = response.get_json()
    assert "error" in payload
    assert "db unavailable" in payload["error"]


def test_main_starts_server() -> None:
    with patch("app.app.run") as run_mock:
        main()
    run_mock.assert_called_once_with(host="127.0.0.1", port=5000, debug=True)
