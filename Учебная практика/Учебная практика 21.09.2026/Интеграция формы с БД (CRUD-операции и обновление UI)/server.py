"""HTTP-сервер: страницы приложения и API партнёров."""
import json
import mimetypes
import os
import re
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit

import psycopg2
from psycopg2 import errors

import db

ROOT = Path(__file__).resolve().parents[1]
HOST = os.environ.get("HOST", "127.0.0.1")
PORT = int(os.environ.get("PORT", "8000"))
PARTNER_TYPES = {"ООО", "ЗАО", "ИП", "ТК", "Другое"}

# Все файлы интерфейса находятся в этой практике.
STATIC_FILES = {
    "/ui/app.js": ROOT / "Проектирование многооконной архитектуры и навигации" / "app.js",
    "/ui/style.css": ROOT / "Проектирование многооконной архитектуры и навигации" / "style.css",
    "/ui/resources/logo.png": ROOT / "Проектирование многооконной архитектуры и навигации" / "resources" / "logo.png",
    "/ui/resources/icon.png": ROOT / "Проектирование многооконной архитектуры и навигации" / "resources" / "icon.png",
    "/form/partner.js": ROOT / "Разработка формы добавления\\редактирования партнера" / "partner.js",
    "/form/partner.css": ROOT / "Разработка формы добавления\\редактирования партнера" / "partner.css",
    "/dialogs.js": ROOT / "Обработка исключений и интерактивные уведомления (UX\\UI)" / "dialogs.js",
    "/dialogs.css": ROOT / "Обработка исключений и интерактивные уведомления (UX\\UI)" / "dialogs.css",
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
                raise ValueError
            data = json.loads(self.rfile.read(length))
            if not isinstance(data, dict):
                raise ValueError
            return data
        except (ValueError, json.JSONDecodeError):
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
            self._send_json({"error": "База данных недоступна. Проверьте подключение и повторите попытку."}, 503)
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
                self._send_json({"error": "Партнёр не найден."}, 404)
                return
            else:
                status = 200

            conn.commit()
            self._send_json({"partner_id": partner_id}, status)
        except errors.UniqueViolation:
            if conn is not None:
                conn.rollback()
            self._send_json({"error": "Такой ИНН или email уже есть в базе. Проверьте введённые данные."}, 409)
        except psycopg2.Error:
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
        elif re.fullmatch(r"/api/partners/[0-9]+", path):
            self._send_partners(int(path.rsplit("/", 1)[1]))
        elif path == "/":
            self._send_file(ROOT / "Проектирование многооконной архитектуры и навигации" / "index.html")
        elif path == "/partner/new" or re.fullmatch(r"/partner/[0-9]+", path):
            self._send_file(ROOT / "Разработка формы добавления\\редактирования партнера" / "partner.html")
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
