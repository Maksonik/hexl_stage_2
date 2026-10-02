"""HTTP-сервер практики 28.09.2026."""
import json
import logging
import mimetypes
import os
import re
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit

import psycopg2
from psycopg2 import errors

ROOT = Path(__file__).resolve().parents[1]
HISTORY = ROOT / "Разработка интерфейса истории реализации продукции"
CORE = ROOT / "Разработка ядра алгоритма расчета материалов"
INTEGRATION = ROOT / "Интеграция метода расчета и комплексное тестирование"
sys.path.insert(0, str(CORE))

import db
from materials import calculate_materials

HOST = os.environ.get("HOST", "127.0.0.1")
PORT = int(os.environ.get("PORT", "8000"))
PARTNER_TYPES = {"ООО", "ЗАО", "ИП", "ТК", "Другое"}
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

# Пути к страницам и ресурсам ограничены файлами этой практики.
STATIC_FILES = {
    "/ui/app.js": HISTORY / "app.js",
    "/ui/style.css": HISTORY / "style.css",
    "/ui/history.js": HISTORY / "history.js",
    "/ui/history.css": HISTORY / "history.css",
    "/ui/resources/logo.png": HISTORY / "resources" / "logo.png",
    "/ui/resources/icon.png": HISTORY / "resources" / "icon.png",
    "/form/partner.js": INTEGRATION / "partner.js",
    "/form/partner.css": INTEGRATION / "partner.css",
    "/calculator.js": INTEGRATION / "calculator.js",
    "/calculator.css": INTEGRATION / "calculator.css",
    "/dialogs.js": INTEGRATION / "dialogs.js",
    "/dialogs.css": INTEGRATION / "dialogs.css",
}


def validate_partner(data):
    if not isinstance(data, dict):
        return None, "Форма отправила данные в неверном формате."

    required = {
        "company_name": "Введите наименование партнёра.",
        "partner_type": "Выберите тип партнёра.",
        "inn": "Введите ИНН.",
        "contact_email": "Введите email.",
    }
    cleaned = {}
    for key, message in required.items():
        value = data.get(key)
        if not isinstance(value, str) or not value.strip():
            return None, message
        cleaned[key] = value.strip()

    if cleaned["partner_type"] not in PARTNER_TYPES:
        return None, "Выберите тип партнёра из списка."
    inn = cleaned["inn"]
    if not (inn.isdigit() and len(inn) in (10, 12)):
        return None, "ИНН должен содержать 10 или 12 цифр."
    rating = data.get("rating")
    if isinstance(rating, bool) or not isinstance(rating, int) or rating < 0:
        return None, "Рейтинг должен быть целым числом от 0. Удалите дробную часть или знак минус."

    cleaned["rating"] = rating
    for key in ("phone", "address", "director_name"):
        value = data.get(key, "")
        cleaned[key] = value.strip() if isinstance(value, str) else ""
    return cleaned, None


class Handler(BaseHTTPRequestHandler):
    def _send_json(self, data, status=200):
        body = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _read_json(self):
        try:
            length = int(self.headers.get("Content-Length", "0"))
            if length < 1 or length > 65536:
                raise ValueError("недопустимая длина запроса")
            data = json.loads(self.rfile.read(length))
            if not isinstance(data, dict):
                raise ValueError("ожидался объект JSON")
            return data
        except ValueError as error:
            logger.warning("Некорректные данные запроса: %s", error)
            self._send_json({"error": "Не удалось прочитать данные формы."}, 400)
            return None

    def _read_partner(self):
        payload = self._read_json()
        if payload is None:
            return None
        data, error = validate_partner(payload)
        if error:
            self._send_json({"error": error}, 400)
            return None
        return data

    def _send_partners(self, partner_id=None):
        conn = None
        try:
            conn = db.connect()
            if partner_id is None:
                self._send_json(db.get_partner_sales_summary(conn))
            else:
                partner = db.get_partner(conn, partner_id)
                if partner is None:
                    self._send_json({"error": "Партнёр не найден."}, 404)
                else:
                    self._send_json(partner)
        except psycopg2.Error:
            logger.exception("Не удалось загрузить партнёров")
            self._send_json({"error": "База данных недоступна. Проверьте подключение и повторите попытку."}, 503)
        finally:
            if conn is not None:
                conn.close()

    def _send_sales(self, partner_id):
        conn = None
        try:
            conn = db.connect()
            partner = db.get_partner(conn, partner_id)
            if partner is None:
                self._send_json({"error": "Партнёр не найден."}, 404)
                return
            sales = db.get_partner_sales(conn, partner_id)
            self._send_json({"partner": partner["company_name"], "sales": sales})
        except psycopg2.Error:
            logger.exception("Не удалось загрузить историю продаж партнёра %s", partner_id)
            self._send_json({"error": "База данных недоступна. Проверьте подключение и повторите попытку."}, 503)
        finally:
            if conn is not None:
                conn.close()

    def _send_catalogs(self):
        conn = None
        try:
            conn = db.connect()
            self._send_json(db.get_catalogs(conn))
        except psycopg2.Error:
            logger.exception("Не удалось загрузить справочники")
            self._send_json({"error": "База данных недоступна. Проверьте подключение и повторите попытку."}, 503)
        finally:
            if conn is not None:
                conn.close()

    def _calculate(self):
        data = self._read_json()
        if data is None:
            return
        try:
            result = calculate_materials(
                data.get("product_type_id"),
                data.get("material_type_id"),
                data.get("quantity"),
                data.get("param_1"),
                data.get("param_2"),
            )
            self._send_json({"result": result})
        except psycopg2.Error:
            logger.exception("Не удалось рассчитать количество материала")
            self._send_json({"error": "База данных недоступна. Проверьте подключение и повторите попытку."}, 503)

    def _save_partner(self, data, partner_id=None):
        conn = None
        try:
            conn = db.connect()
            if partner_id is None:
                partner_id = db.create_partner(conn, data)
                status = 201
            elif not db.update_partner(conn, partner_id, data):
                self._send_json({"error": "Партнёр не найден."}, 404)
                return
            else:
                status = 200
            conn.commit()
            self._send_json({"partner_id": partner_id}, status)
        except errors.UniqueViolation:
            logger.exception("ИНН или email партнёра уже существует")
            if conn is not None:
                conn.rollback()
            self._send_json({"error": "Такой ИНН или email уже есть в базе. Проверьте введённые данные."}, 409)
        except psycopg2.Error:
            logger.exception("Не удалось сохранить партнёра")
            if conn is not None:
                conn.rollback()
            self._send_json({"error": "База данных недоступна. Проверьте подключение и повторите попытку."}, 503)
        finally:
            if conn is not None:
                conn.close()

    def do_GET(self):
        path = urlsplit(self.path).path
        if path == "/api/partners":
            self._send_partners()
        elif re.fullmatch(r"/api/partners/[0-9]+/sales", path):
            self._send_sales(int(path.split("/")[3]))
        elif re.fullmatch(r"/api/partners/[0-9]+", path):
            self._send_partners(int(path.rsplit("/", 1)[1]))
        elif path == "/api/catalogs":
            self._send_catalogs()
        elif path == "/":
            self._send_file(HISTORY / "index.html")
        elif re.fullmatch(r"/partner/[0-9]+/history", path):
            self._send_file(HISTORY / "history.html")
        elif path == "/partner/new" or re.fullmatch(r"/partner/[0-9]+", path):
            self._send_file(INTEGRATION / "partner.html")
        elif path == "/calculator":
            self._send_file(INTEGRATION / "calculator.html")
        elif path in STATIC_FILES:
            self._send_file(STATIC_FILES[path])
        else:
            self.send_error(404)

    def do_POST(self):
        path = urlsplit(self.path).path
        if path == "/api/partners":
            data = self._read_partner()
            if data is not None:
                self._save_partner(data)
        elif path == "/api/materials/calculate":
            self._calculate()
        else:
            self.send_error(404)

    def do_PUT(self):
        path = urlsplit(self.path).path
        if not re.fullmatch(r"/api/partners/[0-9]+", path):
            self.send_error(404)
            return
        data = self._read_partner()
        if data is not None:
            self._save_partner(data, int(path.rsplit("/", 1)[1]))

    def _send_file(self, path):
        if not path.is_file():
            self.send_error(404)
            return
        body = path.read_bytes()
        content_type = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
        if content_type.startswith("text/") or content_type == "application/javascript":
            content_type += "; charset=utf-8"
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


def main():
    server = ThreadingHTTPServer((HOST, PORT), Handler)
    print(f"Сервер запущен: http://{HOST}:{PORT}/")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nОстановка сервера")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
