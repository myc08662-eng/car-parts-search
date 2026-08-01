import json
import mysql.connector
from app.config import get_settings
from app.utils.transliterate import transliterate   
import os

settings = get_settings()

def get_car_id(cursor, brand, model, generation):
    cursor.execute(
        "SELECT id FROM cars WHERE brand = %s AND model = %s AND (generation = %s OR (generation IS NULL AND %s IS NULL))",
        (brand, model, generation, generation)
    )
    row = cursor.fetchone()
    return row[0] if row else None

def get_category_id(cursor, cat_name):
    cursor.execute("SELECT id FROM categories WHERE name = %s", (cat_name,))
    row = cursor.fetchone()
    return row[0] if row else None

def get_or_create_part(cursor, part_name, category_id):
    cursor.execute("SELECT id FROM parts WHERE name = %s AND category_id = %s", (part_name, category_id))
    row = cursor.fetchone()
    if row:
        return row[0]
    cursor.execute("INSERT INTO parts (name, category_id) VALUES (%s, %s)", (part_name, category_id))
    return cursor.lastrowid

def load_data():
    conn = mysql.connector.connect(
        host=settings.DB_HOST,
        port=settings.DB_PORT,
        user=settings.DB_USER,
        password=settings.DB_PASSWORD,
        database=settings.DB_NAME
    )
    cursor = conn.cursor()
    
    #Данные из JSON
    json_path = os.path.join(os.path.dirname(__file__), "data", "parts.json")
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    for item in data:
        brand, model, generation = item['car'].split()  
        if len(brand.split()) > 1:
            pass
        pass
    
    conn.commit()
    cursor.close()
    conn.close()

if __name__ == "__main__":
    load_data()