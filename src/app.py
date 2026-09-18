import sys
from pathlib import Path

from flask import Flask, jsonify, send_from_directory

SRC_DIR = Path(__file__).resolve().parent
WEB_DIR = SRC_DIR.parent / "web"
sys.path.insert(0, str(SRC_DIR))

from partner_sales import list_partners_with_discount

app = Flask(__name__, static_folder=str(WEB_DIR), static_url_path="")


@app.get("/")
def index():
    return send_from_directory(WEB_DIR, "index.html")


@app.get("/api/partners")
def api_partners():
    try:
        partners = list_partners_with_discount()
        return jsonify(partners)
    except Exception as error:
        return jsonify({"error": str(error)}), 500


def main() -> None:
    app.run(host="127.0.0.1", port=5000, debug=True)


if __name__ == "__main__":  # pragma: no cover
    main()
