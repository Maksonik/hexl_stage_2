# Учебная практика 28.09.2026

Нужные исходники и данные скопированы внутрь этой практики. Для неё используется отдельная база `practice_db_2809`; файлы прошлых практик при запуске не нужны.

## Требования

- Python 3.10+
- PostgreSQL 16+
- `psycopg2-binary` (`python3 -m pip install psycopg2-binary`)

## Подготовка базы

Перейдите в папку «Разработка ядра алгоритма расчета материалов». Импорт запускайте из неё, потому что файлы CSV и TXT в командах `\copy` указаны относительно текущей папки.

```bash
createdb practice_db_2809
psql -d practice_db_2809 -f schema.sql
psql -d practice_db_2809 -f import_data.sql
psql -d practice_db_2809 -f seed_sales.sql
psql -d practice_db_2809 -f seed_catalogs.sql
psql -d practice_db_2809 -f verification_queries.sql
```

Схема создаёт таблицы партнёров, товаров, продаж и две таблицы для рассчёт. Коэффициенты типов продукции равны 1,00 и 1,50, проценты брака материалов — 0% и 5%. Они не связаны с уже импортированными товарами: это отдельные варианты для калькулятора.

Если параметры подключения отличаются, задайте `PRACTICE_DB_DSN`, например:

```bash
export PRACTICE_DB_DSN="dbname=practice_db_2809 user=postgres"
```

## Запуск

Из корня практики:

```bash
python3 "Интеграция метода расчета и комплексное тестирование/server.py"
```

Откройте <http://127.0.0.1:8000/>. На главной странице можно выбрать партнёра и открыть историю продаж, перейти в карточку или открыть калькулятор. По умолчанию сервер слушает `127.0.0.1:8000`; адрес и порт меняются переменными `HOST` и `PORT`.

## Проверки

Из корня практики:

```bash
python3 -m unittest discover -v -s "Модульное тестирование (Unit Testing) и аудит безопасности" -p "test_*.py"
```

API: `GET /api/partners`, `GET /api/partners/{id}`, `GET /api/partners/{id}/sales`, `GET /api/catalogs`, `POST /api/materials/calculate`, `POST /api/partners`, `PUT /api/partners/{id}`. Для расчёта передаются `product_type_id`, `material_type_id`, `quantity`, `param_1`, `param_2`; результат — `{"result": число}`. Все SQL-запросы с пользовательскими значениями используют параметры.
