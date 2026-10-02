import sys
import unittest
from decimal import Decimal
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "Разработка ядра алгоритма расчета материалов"))

from materials import calculate_materials


class TestMaterials(unittest.TestCase):
    @patch("db.get_material_factors", return_value=(Decimal("1.50"), Decimal("5.00")))
    def test_normal(self, lookup):
        self.assertEqual(calculate_materials(2, 2, 2, 2.0, 3.0), 19)
        lookup.assert_called_once_with(2, 2)

    @patch("db.get_material_factors", return_value=(Decimal("1.00"), Decimal("5.00")))
    def test_round_up(self, lookup):
        self.assertEqual(calculate_materials(1, 2, 1, 1.0, 1.0), 2)

    @patch("db.get_material_factors", return_value=None)
    def test_unknown_product_type(self, lookup):
        self.assertEqual(calculate_materials(99, 1, 1, 1.0, 1.0), -1)

    @patch("db.get_material_factors", return_value=None)
    def test_unknown_material_type(self, lookup):
        self.assertEqual(calculate_materials(1, 99, 1, 1.0, 1.0), -1)

    @patch("db.get_material_factors")
    def test_negative_sizes(self, lookup):
        self.assertEqual(calculate_materials(1, 1, 1, -1.0, 2.0), -1)
        self.assertEqual(calculate_materials(1, 1, 1, 1.0, -2.0), -1)
        lookup.assert_not_called()

    @patch("db.get_material_factors")
    def test_zero_quantity(self, lookup):
        self.assertEqual(calculate_materials(1, 1, 0, 1.0, 1.0), -1)
        self.assertEqual(calculate_materials(1, 1, -1, 1.0, 1.0), -1)
        lookup.assert_not_called()

    @patch("db.get_material_factors")
    def test_zero_or_invalid_sizes(self, lookup):
        self.assertEqual(calculate_materials(1, 1, 1, 0, 1.0), -1)
        self.assertEqual(calculate_materials(1, 1, 1, float("nan"), 1.0), -1)
        self.assertEqual(calculate_materials(1, 1, 1, "2", 1.0), -1)
        lookup.assert_not_called()


if __name__ == "__main__":
    unittest.main()
