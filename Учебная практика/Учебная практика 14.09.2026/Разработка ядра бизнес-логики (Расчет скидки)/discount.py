"""Расчет индивидуального процента скидки партнера."""


def calculate_partner_discount(total_quantity: int) -> int:
    if total_quantity < 10000:
        return 0
    if total_quantity < 50000:
        return 5
    if total_quantity < 300000:
        return 10
    return 15
