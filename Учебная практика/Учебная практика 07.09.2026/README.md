# Учебная практика 07.09.2026

## Требования
- PostgreSQL 16+

## Полный цикл запуска

```bash
# 1. Создать БД
createdb practice_db

# 2. Создать таблицы
psql -d practice_db -f "Написание DDL-скрипта (База данных в коде)/schema.sql"

# 3. Импорт (запуск из папки с данными, т.к. \copy использует относительные пути)
cd "Подготовка данных и импорт (ETL)"
psql -d practice_db -f import_data.sql

# 4. Проверка
psql -d practice_db -f verification_queries.sql

# 5. Тест запросов приложения
psql -d practice_db -f "../Разработка проверочных SQL-запросов (Эмуляция бэкенда)/queries.sql"
```

---

