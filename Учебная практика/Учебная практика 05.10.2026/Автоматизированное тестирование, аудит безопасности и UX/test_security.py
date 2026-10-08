import project_paths

import unittest
from unittest.mock import MagicMock

import db

INJECTION = "'; DROP TABLE partners; --"


class TestSqlParameters(unittest.TestCase):
    def setUp(self):
        self.conn = MagicMock()
        self.cursor = self.conn.cursor.return_value.__enter__.return_value
        self.cursor.fetchone.return_value = None
        self.cursor.fetchall.return_value = []

    def test_partner_fields_go_to_parameters(self):
        data = {
            "partner_name": INJECTION,
            "partner_type": "ООО",
            "rating": 0,
            "inn": "7701234567",
            "address": INJECTION,
            "director_name": INJECTION,
            "phone": "",
            "email": "a@b.ru",
        }
        db.update_partner(self.conn, 1, data)
        query, params = self.cursor.execute.call_args.args
        self.assertNotIn("DROP", query)
        self.assertIn(INJECTION, params)

    def test_ids_go_to_parameters(self):
        db.get_partner(self.conn, INJECTION)
        db.get_partner_sales(self.conn, INJECTION)
        for call in self.cursor.execute.call_args_list:
            query, params = call.args
            self.assertNotIn("DROP", query)
            self.assertEqual(params, (INJECTION,))


if __name__ == "__main__":
    unittest.main()
