import unittest

from discount import calculate_partner_discount


class TestCalculatePartnerDiscount(unittest.TestCase):
    def test_zero_quantity_returns_zero(self):
        self.assertEqual(calculate_partner_discount(0), 0)

    def test_less_than_10000_returns_zero(self):
        self.assertEqual(calculate_partner_discount(9999), 0)

    def test_boundary_10000_returns_five(self):
        self.assertEqual(calculate_partner_discount(10000), 5)

    def test_boundary_49999_returns_five(self):
        self.assertEqual(calculate_partner_discount(49999), 5)

    def test_boundary_50000_returns_ten(self):
        self.assertEqual(calculate_partner_discount(50000), 10)

    def test_boundary_299999_returns_ten(self):
        self.assertEqual(calculate_partner_discount(299999), 10)

    def test_boundary_300000_returns_fifteen(self):
        self.assertEqual(calculate_partner_discount(300000), 15)

    def test_large_value_returns_fifteen(self):
        self.assertEqual(calculate_partner_discount(300001), 15)
        self.assertEqual(calculate_partner_discount(1000000), 15)


if __name__ == "__main__":
    unittest.main()
