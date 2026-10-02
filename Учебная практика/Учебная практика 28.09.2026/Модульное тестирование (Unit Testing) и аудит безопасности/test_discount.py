import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "Интеграция метода расчета и комплексное тестирование"))
sys.path.insert(0, str(ROOT / "Разработка ядра алгоритма расчета материалов"))

import unittest

from discount import calculate_partner_discount


class TestDiscount(unittest.TestCase):
    def test_zero(self):
        self.assertEqual(calculate_partner_discount(0), 0)

    def test_9999(self):
        self.assertEqual(calculate_partner_discount(9999), 0)

    def test_10000(self):
        self.assertEqual(calculate_partner_discount(10000), 5)

    def test_49999(self):
        self.assertEqual(calculate_partner_discount(49999), 5)

    def test_50000(self):
        self.assertEqual(calculate_partner_discount(50000), 10)

    def test_299999(self):
        self.assertEqual(calculate_partner_discount(299999), 10)

    def test_300000(self):
        self.assertEqual(calculate_partner_discount(300000), 15)

    def test_big_number(self):
        self.assertEqual(calculate_partner_discount(300001), 15)
        self.assertEqual(calculate_partner_discount(1000000), 15)


if __name__ == "__main__":
    unittest.main()
