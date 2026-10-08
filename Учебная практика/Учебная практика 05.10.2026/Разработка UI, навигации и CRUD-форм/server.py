"""HTTP-сервер практики 05.10.2026: окна приложения и JSON API."""
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

UI = Path(__file__).resolve().parent
CORE = UI.parent / "Реализация ядра бизнес-логики (Расчеты и алгоритмы)"
sys.path.insert(0, str(CORE))

import db
from discount import calculate_partner_discount

HOST = os.environ.get("HOST", "127.0.0.1")
PORT = int(os.environ.get("PORT", "8000"))
PARTNER_TYPES = {"ООО", "АО", "ЗАО", "ИП", "Другое"}
DB_ERROR = "База данных недоступна."
DB_STEPS = [
    "Убедитесь, что сервер PostgreSQL запущен.",
    "Проверьте параметры подключения в переменной PRACTICE_DB_DSN.",
    "Повторите действие. Если ошибка осталась, обратитесь к администратору.",
]
INPUT_STEPS = [
    "Исправьте поле, указанное в сообщении.",
    "Нажмите «Сохранить» ещё раз.",
]
DUPLICATE_STEPS = [
    "Проверьте ИНН и email в форме.",
    "Если партнёр уже есть в списке, вернитесь и откройте его карточку.",
    "Иначе исправьте значение и нажмите «Сохранить» ещё раз.",
]
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

# Наружу отдаются только перечисленные файлы интерфейса.
STATIC_FILES = {
    "/static/" + name: UI / name
    for name in (
        "style.css",
        "api.js",
        "dialogs.css",
        "dialogs.js",
        "main_window.js",
        "partner_edit_window.css",
        "partner_edit_window.js",
        "partner_history_window.css",
        "partner_history_window.js",
        "resources/logo.png",
        "resources/icon.png",
    )
}


def validate_partner(data):
    if not isinstance(data, dict):
        return None, "Форма отправила данные в неверном формате."

    required = {
        "partner_name": "Введите наименование партнёра.",
        "partner_type": "Выберите тип партнёра.",
        "inn": "Введите ИНН.",
        "email": "Введите email.",
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
    if not re.fullmatch(r"[0-9]{10}|[0-9]{12}", inn):
        return None, "ИНН должен содержать 10 или 12 цифр."
    rating = data.get("rating")
    if isinstance(rating, bool) or not isinstance(rating, int) or rating < 0:
        return None, "Рейтинг должен быть целым числом от 0. Удалите дробную часть или знак минус."

    cleaned["rating"] = rating
    for key in ("phone", "address", "director_name"):
        value = data.get(key, "")
        cleaned[key] = value.strip() if isinstance(value, str) else ""
    return cleaned, None


def with_discount(partner):
    partner["discount_percent"] = calculate_partner_discount(partner["total_quantity"])
    return partner


class Handler(BaseHTTPRequestHandler):
    def _send_error(self, status, message, steps):
        self._send_json({"error": message, "steps": steps}, status)

    def _send_json(self, data, status=200):
        body = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _read_partner(self):
        try:
            length = int(self.headers.get("Content-Length", "0"))
            if length < 1 or length > 65536:
                raise ValueError("недопустимая длина запроса")
            payload = json.loads(self.rfile.read(length))
        except ValueError as error:
            logger.warning("Некорректные данные запроса: %s", error)
            self._send_error(400, "Не удалось прочитать данные формы.", ["Обновите страницу.", "Заполните форму и сохраните её заново."])
            return None
        data, error = validate_partner(payload)
        if error:
            self._send_error(400, error, INPUT_STEPS)
            return None
        return data

    def _send_partners(self, partner_id=None):
        conn = None
        try:
            conn = db.connect()
            if partner_id is None:
                self._send_json([with_discount(partner) for partner in db.get_partners(conn)])
                return
            partner = db.get_partner(conn, partner_id)
            if partner is None:
                self._send_error(404, "Партнёр не найден.", ["Вернитесь к списку партнёров.", "Нажмите «Обновить» и выберите партнёра заново."])
            else:
                self._send_json(with_discount(partner))
        except psycopg2.Error:
            logger.exception("Не удалось загрузить партнёров")
            self._send_error(503, DB_ERROR, DB_STEPS)
        finally:
            if conn is not None:
                conn.close()

    def _send_sales(self, partner_id):
        conn = None
        try:
            conn = db.connect()
            partner = db.get_partner(conn, partner_id)
            if partner is None:
                self._send_error(404, "Партнёр не найден.", ["Вернитесь к списку партнёров.", "Нажмите «Обновить» и выберите партнёра заново."])
                return
            sales = db.get_partner_sales(conn, partner_id)
            self._send_json({"partner": partner["partner_name"], "sales": sales})
        except psycopg2.Error:
            logger.exception("Не удалось загрузить историю продаж партнёра %s", partner_id)
            self._send_error(503, DB_ERROR, DB_STEPS)
        finally:
            if conn is not None:
                conn.close()

    def _save_partner(self, data, partner_id=None):
        conn = None
        try:
            conn = db.connect()
            if partner_id is None:
                partner_id = db.create_partner(conn, data)
                status = 201
            elif not db.update_partner(conn, partner_id, data):
                self._send_error(404, "Партнёр не найден.", ["Вернитесь к списку партнёров.", "Нажмите «Обновить» и выберите партнёра заново."])
                return
            else:
                status = 200
            conn.commit()
            self._send_json({"partner_id": partner_id}, status)
        except errors.UniqueViolation:
            logger.warning("ИНН или email партнёра уже существует")
            self._send_error(409, "Партнёр с таким ИНН или email уже есть в базе.", DUPLICATE_STEPS)
        except psycopg2.Error:
            logger.exception("Не удалось сохранить партнёра")
            self._send_error(503, DB_ERROR, DB_STEPS)
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
        elif path == "/":
            self._send_file(UI / "main_window.html")
        elif re.fullmatch(r"/partner/[0-9]+/history", path):
            self._send_file(UI / "partner_history_window.html")
        elif path == "/partner/new" or re.fullmatch(r"/partner/[0-9]+", path):
            self._send_file(UI / "partner_edit_window.html")
        elif path in STATIC_FILES:
            self._send_file(STATIC_FILES[path])
        else:
            self.send_error(404)

    def do_POST(self):
        if urlsplit(self.path).path != "/api/partners":
            self.send_error(404)
            return
        data = self._read_partner()
        if data is not None:
            self._save_partner(data)

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
