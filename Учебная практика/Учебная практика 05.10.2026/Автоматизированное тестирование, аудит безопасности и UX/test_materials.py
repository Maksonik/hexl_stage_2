import project_paths

import unittest
from decimal import Decimal
from unittest.mock import patch

from materials import calculate_materials


class TestMaterials(unittest.TestCase):
    @patch("db.get_material_factors", return_value=(Decimal("1.50"), Decimal("5.00")))
    def test_basic_calculation(self, lookup):
        # 2 * 2.0 * 3.0 * 1.5 * 1.05 = 18.9 -> 19
        self.assertEqual(calculate_materials(2, 2, 2, 2.0, 3.0), 19)
        lookup.assert_called_once_with(2, 2)

    @patch("db.get_material_factors", return_value=(Decimal("1.00"), Decimal("0.00")))
    def test_without_defect(self, lookup):
        self.assertEqual(calculate_materials(1, 1, 5, 2, 3), 30)

    @patch("db.get_material_factors", return_value=(Decimal("1.00"), Decimal("5.00")))
    def test_round_up_small_fraction(self, lookup):
        # 1.05 при обычном округлении дало бы 1, расход всегда округляется вверх.
        self.assertEqual(calculate_materials(1, 2, 1, 1.0, 1.0), 2)

    @patch("db.get_material_factors", return_value=(Decimal("1.00"), Decimal("0.01")))
    def test_round_up_tiny_fraction(self, lookup):
        self.assertEqual(calculate_materials(1, 1, 10, 1, 1), 11)

    @patch("db.get_material_factors", return_value=(Decimal("1.00"), Decimal("0.00")))
    def test_whole_result_not_increased(self, lookup):
        # 10 * 0.1 * 3 во float равно 3.0000000000000004; расчёт в Decimal даёт ровно 3.
        self.assertEqual(calculate_materials(1, 1, 10, 0.1, 3), 3)

    @patch("db.get_material_factors", return_value=None)
    def test_unknown_product_type(self, lookup):
        self.assertEqual(calculate_materials(99, 1, 1, 1.0, 1.0), -1)
        lookup.assert_called_once_with(99, 1)

    @patch("db.get_material_factors", return_value=None)
    def test_unknown_material_type(self, lookup):
        self.assertEqual(calculate_materials(1, 99, 1, 1.0, 1.0), -1)

    @patch("db.get_material_factors")
    def test_negative_parameters(self, lookup):
        self.assertEqual(calculate_materials(1, 1, 1, -1.0, 2.0), -1)
        self.assertEqual(calculate_materials(1, 1, 1, 1.0, -2.0), -1)
        self.assertEqual(calculate_materials(1, 1, -1, 1.0, 1.0), -1)
        self.assertEqual(calculate_materials(-1, 1, 1, 1.0, 1.0), -1)
        self.assertEqual(calculate_materials(1, -1, 1, 1.0, 1.0), -1)
        lookup.assert_not_called()

    @patch("db.get_material_factors")
    def test_zero_values(self, lookup):
        self.assertEqual(calculate_materials(1, 1, 0, 1.0, 1.0), -1)
        self.assertEqual(calculate_materials(1, 1, 1, 0, 1.0), -1)
        lookup.assert_not_called()

    @patch("db.get_material_factors")
    def test_wrong_types(self, lookup):
        self.assertEqual(calculate_materials(1, 1, 1, float("nan"), 1.0), -1)
        self.assertEqual(calculate_materials(1, 1, 1, float("inf"), 1.0), -1)
        self.assertEqual(calculate_materials(1, 1, 1, "2", 1.0), -1)
        self.assertEqual(calculate_materials(1, 1, 1.5, 1.0, 1.0), -1)
        self.assertEqual(calculate_materials(None, 1, 1, 1.0, 1.0), -1)
        self.assertEqual(calculate_materials(True, 1, 1, 1.0, 1.0), -1)
        lookup.assert_not_called()


if __name__ == "__main__":
    unittest.main()
