# hexl_stage_2

CRM: список партнеров и расчет скидок.

## Запуск БД

```bash
docker compose up -d
```

Параметры подключения — в `.env.example` (по умолчанию `partners` / `partners` @ `localhost:5432`).

## Установка и тесты

```bash
uv sync
uv run pytest
```

## Запуск приложения

```bash
uv run python src/app.py
```

Откройте http://127.0.0.1:5000 — список партнеров и скидок из PostgreSQL.
