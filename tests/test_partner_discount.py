import pytest

from partner_discount import calculate_partner_discount


@pytest.mark.parametrize(
    ("total_quantity", "expected_discount"),
    [
        (9_999, 0),
        (10_000, 5),
        (49_999, 5),
        (50_000, 10),
        (299_999, 10),
        (300_000, 15),
        (0, 0),
        (1_000_000, 15),
    ],
)
def test_calculate_partner_discount(total_quantity: int, expected_discount: int) -> None:
    assert calculate_partner_discount(total_quantity) == expected_discount
