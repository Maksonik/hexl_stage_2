"""Финальный демонстрационный тест приложения.

Проверяет связку БД + бизнес-логика и отказоустойчивость:
партнер без истории продаж получает скидку 0% без ошибок.
Также выполняет стресс-тест запросов к БД.
"""
import os
import sys
import time

PARENT = os.path.dirname(__file__)
sys.path.insert(0, os.path.join(PARENT, "..", "Интеграция с БД и агрегация данных (SQL + Backend)"))

import db

ITERATIONS = 200


def find_partner_without_history(conn):
    with conn.cursor() as cur:
        cur.execute(
            "SELECT partner_id, company_name FROM partners p "
            "WHERE NOT EXISTS (SELECT 1 FROM sales s WHERE s.partner_id = p.partner_id) "
            "LIMIT 1"
        )
        return cur.fetchone()


def test_partner_without_history():
    conn = db.connect()
    try:
        partner = find_partner_without_history(conn)
        assert partner is not None, "В БД нет партнера без истории продаж"
        data = db.get_partner_with_discount(conn, partner[0])
        assert data is not None
        assert data["total_quantity"] == 0
        assert data["discount_percent"] == 0
        print(f"[ok] {partner[1]}: история продаж отсутствует, скидка 0%")
    finally:
        conn.close()


def test_all_partners_have_discount():
    conn = db.connect()
    try:
        partners = db.get_partners_with_discount(conn)
        assert partners, "Список партнеров пуст"
        for partner in partners:
            assert 0 <= partner["discount_percent"] <= 15
            assert partner["total_quantity"] >= 0
        print(f"[ok] корректная скидка у всех {len(partners)} партнеров")
    finally:
        conn.close()


def demo_table():
    conn = db.connect()
    try:
        partners = db.get_partners_with_discount(conn)
        print(f"{'Компания':<28}{'Объем, шт.':>12}{'Скидка':>8}")
        for partner in partners:
            print(f"{partner['company_name']:<28}{partner['total_quantity']:>12}{partner['discount_percent']:>7}%")
    finally:
        conn.close()


def stress_test():
    conn = db.connect()
    try:
        start = time.perf_counter()
        for _ in range(ITERATIONS):
            partners = db.get_partners_with_discount(conn)
            assert partners
        elapsed = time.perf_counter() - start
        avg_ms = elapsed / ITERATIONS * 1000
        print(f"[ok] стресс-тест: {ITERATIONS} запросов за {elapsed:.2f} с ({avg_ms:.2f} мс на запрос)")
    finally:
        conn.close()


def main():
    test_partner_without_history()
    test_all_partners_have_discount()
    demo_table()
    stress_test()
    print("\nВсе проверки пройдены.")


if __name__ == "__main__":
    main()