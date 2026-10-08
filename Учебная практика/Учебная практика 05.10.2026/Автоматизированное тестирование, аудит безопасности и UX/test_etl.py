import project_paths

import unittest
from datetime import date
from decimal import Decimal

from etl import clean_text, extract_and_clean, normalize_date, partner_type


class TestCleaning(unittest.TestCase):
    def test_trim_and_inner_spaces(self):
        self.assertEqual(clean_text('  ООО "Альфа" '), 'ООО "Альфа"')
        self.assertEqual(clean_text("Петров  A.B."), "Петров A.B.")

    def test_partner_type_from_name(self):
        self.assertEqual(partner_type('АО "Технолоджис"'), "АО")
        self.assertEqual(partner_type("Ромашка"), "Другое")

    def test_date_formats(self):
        for value in ("25.10.2023", "25-10-2023", "2023-10-25", "2023/10/25", "2023.10.25", " 2023-10-25 "):
            self.assertEqual(normalize_date(value), date(2023, 10, 25))


class TestRawFiles(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.partners, cls.products, cls.sales, cls.rejected = extract_and_clean()

    def test_partners(self):
        self.assertEqual(
            [(p["partner_name"], p["partner_type"], p["email"]) for p in self.partners],
            [
                ('ООО "Вектор"', "ООО", "vector@mail.ru"),
                ("ИП ...Петров A.B.", "ИП", "petrov@yandex.ru"),
                ('АО "Технолоджис"', "АО", "info@techno.ru"),
                ('ООО "Альфа"', "ООО", "alpha@gmail.com"),
                ("ИП Сидоров И.И.", "ИП", "sidorov@llc.ru"),
            ],
        )

    def test_products(self):
        self.assertEqual(
            [(p["product_name"], p["price"]) for p in self.products],
            [("Ноутбук Pro", Decimal("75000.0")), ("Смартфон X", Decimal("45000.5")), ('Монитор 27"', Decimal("18200.0"))],
        )

    def test_sales_dates(self):
        self.assertEqual(
            [s["sale_date"].isoformat() for s in self.sales],
            ["2023-10-25", "2023-10-26", "2023-10-28", "2023-10-29", "2023-10-30"],
        )

    def test_broken_foreign_key_removed(self):
        self.assertEqual(self.rejected, [1003])
        self.assertNotIn(999, [s["partner_id"] for s in self.sales])


if __name__ == "__main__":
    unittest.main()
