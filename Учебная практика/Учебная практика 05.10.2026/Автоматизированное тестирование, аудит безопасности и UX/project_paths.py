"""Подключает папки с кодом практики, чтобы тесты запускались из любой директории."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ETL = ROOT / "Инфраструктура данных и ETL (База данных в 3NF)"
CORE = ROOT / "Реализация ядра бизнес-логики (Расчеты и алгоритмы)"
UI = ROOT / "Разработка UI, навигации и CRUD-форм"

for folder in (ETL, CORE, UI):
    sys.path.insert(0, str(folder))
