import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import json
import mysql.connector
from app.config import get_settings
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

settings = get_settings()

def get_or_create_category(cursor, name):
    cursor.execute("SELECT id FROM categories WHERE name = %s", (name,))
    row = cursor.fetchone()
    if row:
        return row[0]
    cursor.execute("INSERT INTO categories (name) VALUES (%s)", (name,))
    return cursor.lastrowid

def get_or_create_car(cursor, car_str):
    parts = car_str.split()
    if len(parts) < 2:
        logger.error(f"Некорректное название автомобиля: {car_str}")
        return None
    brand = parts[0]
    model = parts[1]
    generation = parts[2] if len(parts) > 2 else None
    cursor.execute(
        "SELECT id FROM cars WHERE brand = %s AND model = %s AND (generation = %s OR (generation IS NULL AND %s IS NULL))",
        (brand, model, generation, generation)
    )
    row = cursor.fetchone()
    if row:
        return row[0]
    cursor.execute(
        "INSERT INTO cars (brand, model, generation) VALUES (%s, %s, %s)",
        (brand, model, generation)
    )
    return cursor.lastrowid

def get_or_create_part(cursor, name, category_id):
    cursor.execute("SELECT id FROM parts WHERE name = %s AND category_id = %s", (name, category_id))
    row = cursor.fetchone()
    if row:
        return row[0]
    cursor.execute("INSERT INTO parts (name, category_id) VALUES (%s, %s)", (name, category_id))
    return cursor.lastrowid

def insert_or_update_part_link(cursor, part_id, car_id, url, price, vendor):
    cursor.execute(
        "SELECT id FROM part_links WHERE part_id = %s AND car_id = %s",
        (part_id, car_id)
    )
    row = cursor.fetchone()
    if row:
        cursor.execute(
            "UPDATE part_links SET url = %s, price = %s, vendor = %s, is_active = 1 WHERE id = %s",
            (url, price, vendor, row[0])
        )
        return row[0]
    else:
        cursor.execute(
            "INSERT INTO part_links (part_id, car_id, url, price, vendor, is_active, created_at) "
            "VALUES (%s, %s, %s, %s, %s, 1, NOW())",
            (part_id, car_id, url, price, vendor)
        )
        return cursor.lastrowid

def load_data():
    json_path = os.path.join(os.path.dirname(__file__), "data", "parts.json")
    if not os.path.exists(json_path):
        logger.error(f"Файл {json_path} не найден")
        return

    with open(json_path, "r", encoding="utf-8") as f:
        items = json.load(f)

    conn = mysql.connector.connect(
        host=settings.DB_HOST,
        port=settings.DB_PORT,
        user=settings.DB_USER,
        password=settings.DB_PASSWORD,
        database=settings.DB_NAME
    )
    cursor = conn.cursor()
    total = 0
    for item in items:
        try:
            car_str = item["car"]
            category_name = item["category"]
            part_name = item["part_name"]
            price = item.get("price")
            url = item["url"]
            vendor = item.get("vendor")

            category_id = get_or_create_category(cursor, category_name)
            car_id = get_or_create_car(cursor, car_str)
            if not car_id:
                continue
            part_id = get_or_create_part(cursor, part_name, category_id)
            link_id = insert_or_update_part_link(cursor, part_id, car_id, url, price, vendor)
            total += 1
            logger.info(f"Обработано: {part_name} | {car_str} | {price} руб.")
        except Exception as e:
            logger.error(f"Ошибка при обработке {item}: {e}")
            conn.rollback()
            continue

    conn.commit()
    cursor.close()
    conn.close()
    logger.info(f"Загрузка завершена. Обработано {total} записей.")

if __name__ == "__main__":
    load_data()