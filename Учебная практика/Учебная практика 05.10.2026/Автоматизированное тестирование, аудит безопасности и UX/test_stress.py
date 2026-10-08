import project_paths

import json
import threading
import time
import unittest
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from http.server import ThreadingHTTPServer
from unittest.mock import MagicMock, patch

import server

PARTNER = {"partner_id": 1, "partner_name": "ООО Пример", "total_quantity": 50000}


class TestStress(unittest.TestCase):
    def test_500_requests(self):
        # Порт 0 — система сама выдаёт свободный порт; база заменена заглушкой.
        httpd = ThreadingHTTPServer(("127.0.0.1", 0), server.Handler)
        url = f"http://127.0.0.1:{httpd.server_address[1]}/api/partners"
        threading.Thread(target=httpd.serve_forever, daemon=True).start()

        def load(number):
            with urllib.request.urlopen(url, timeout=10) as response:
                return json.loads(response.read())[0]["discount_percent"]

        try:
            with (
                patch.object(server.Handler, "log_message", lambda *args: None),
                patch("db.connect", return_value=MagicMock()),
                patch("db.get_partners", side_effect=lambda conn: [dict(PARTNER)]),
            ):
                started = time.perf_counter()
                with ThreadPoolExecutor(max_workers=25) as pool:
                    results = list(pool.map(load, range(500)))
                elapsed = time.perf_counter() - started
        finally:
            httpd.shutdown()
            httpd.server_close()

        self.assertEqual(results, [10] * 500)
        self.assertLess(elapsed, 30)


if __name__ == "__main__":
    unittest.main()
