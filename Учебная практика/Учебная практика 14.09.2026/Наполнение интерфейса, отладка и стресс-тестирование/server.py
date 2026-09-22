"""HTTP-сервер приложения: отдает UI и JSON API с данными партнеров."""
import json
import mimetypes
import os
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

PARENT = os.path.dirname(__file__)
sys.path.insert(0, os.path.join(PARENT, "..", "Интеграция с БД и агрегация данных (SQL + Backend)"))

import db

HOST = os.environ.get("HOST", "127.0.0.1")
PORT = int(os.environ.get("PORT", "8000"))
UI_DIR = os.path.realpath(os.path.join(PARENT, "..", "Разработка интерфейса (UI) по руководству по стилю"))


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/api/partners":
            self._send_partners()
        else:
            self._send_static()

    def _send_json(self, data, status=200):
        body = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _send_partners(self):
        conn = db.connect()
        try:
            partners = db.get_partners_with_discount(conn)
            self._send_json(partners)
        except Exception as error:
            self._send_json({"error": str(error)}, status=500)
        finally:
            conn.close()

    def _send_static(self):
        path = self.path.lstrip("/")
        if path == "":
            path = "index.html"
        full = os.path.realpath(os.path.join(UI_DIR, path))
        if full != UI_DIR and not full.startswith(UI_DIR + os.sep):
            self.send_error(403)
            return
        if not os.path.isfile(full):
            self.send_error(404)
            return
        mime = mimetypes.guess_type(full)[0] or "application/octet-stream"
        if mime.startswith("text/"):
            mime += "; charset=utf-8"
        with open(full, "rb") as f:
            body = f.read()
        self.send_response(200)
        self.send_header("Content-Type", mime)
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