import unittest

from server import validate_partner


GOOD_DATA = {
    "company_name": "ООО Пример",
    "partner_type": "ООО",
    "inn": "7701234567",
    "contact_email": "partner@example.ru",
    "phone": "+7 (900) 000-00-00",
    "rating": 0,
    "address": "",
    "director_name": "",
}


class TestForm(unittest.TestCase):
    def test_good_data(self):
        data = GOOD_DATA.copy()
        data["company_name"] = "  ООО Пример  "
        result, error = validate_partner(data)
        self.assertIsNone(error)
        self.assertEqual(result["company_name"], "ООО Пример")

    def test_bad_rating(self):
        for rating in (-1, 1.5, "3", True):
            data = GOOD_DATA.copy()
            data["rating"] = rating
            result, error = validate_partner(data)
            self.assertIsNone(result)
            self.assertIn("Рейтинг", error)

    def test_empty_fields(self):
        for field in ("company_name", "partner_type", "inn", "contact_email"):
            data = GOOD_DATA.copy()
            data[field] = " "
            result, error = validate_partner(data)
            self.assertIsNone(result)
            self.assertIsNotNone(error)

    def test_bad_inn(self):
        for inn in ("123", "12345678901", "123456789a"):
            data = GOOD_DATA.copy()
            data["inn"] = inn
            result, error = validate_partner(data)
            self.assertIsNone(result)
            self.assertIn("ИНН", error)

    def test_bad_type(self):
        data = GOOD_DATA.copy()
        data["partner_type"] = "АО"
        result, error = validate_partner(data)
        self.assertIsNone(result)
        self.assertIn("тип партнёра", error)


if __name__ == "__main__":
    unittest.main()
