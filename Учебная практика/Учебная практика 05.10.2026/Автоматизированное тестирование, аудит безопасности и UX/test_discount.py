import project_paths

import unittest

from discount import calculate_partner_discount


class TestDiscount(unittest.TestCase):
    def test_boundaries(self):
        cases = {0: 0, 9999: 0, 10000: 5, 49999: 5, 50000: 10, 299999: 10, 300000: 15, 1000000: 15}
        for total_quantity, percent in cases.items():
            self.assertEqual(calculate_partner_discount(total_quantity), percent)


if __name__ == "__main__":
    unittest.main()
