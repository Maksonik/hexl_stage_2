"""Расчёт количества сырья для производства с учётом брака."""
from decimal import Decimal, InvalidOperation, ROUND_CEILING
import logging

import db

logger = logging.getLogger(__name__)


def calculate_materials(product_type_id, material_type_id, quantity, param_1, param_2):
    ids = (product_type_id, material_type_id, quantity)
    if any(isinstance(value, bool) or not isinstance(value, int) or value <= 0 for value in ids):
        return -1

    if any(isinstance(value, bool) or not isinstance(value, (int, float, Decimal)) for value in (param_1, param_2)):
        return -1

    try:
        sizes = (Decimal(str(param_1)), Decimal(str(param_2)))
        if any(not value.is_finite() or value <= 0 for value in sizes):
            return -1
    except (InvalidOperation, TypeError, ValueError):
        logger.exception("Не удалось прочитать параметры продукции")
        return -1

    factors = db.get_material_factors(product_type_id, material_type_id)
    if factors is None:
        return -1

    coefficient, defect_percent = factors
    try:
        # Считаем в Decimal: во float 10 * 0.1 * 3 даёт 3.0000000000000004, и округление вверх вернуло бы 4.
        total = quantity * sizes[0] * sizes[1] * Decimal(str(coefficient))
        total *= 1 + Decimal(str(defect_percent)) / 100
        return int(total.to_integral_value(rounding=ROUND_CEILING))
    except (InvalidOperation, TypeError, ValueError):
        logger.exception("Не удалось вычислить расход материала")
        return -1
