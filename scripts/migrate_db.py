import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import mysql.connector
from app.config import get_settings
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

settings = get_settings()

def run_migration():
    conn = mysql.connector.connect(
        host=settings.DB_HOST,
        port=settings.DB_PORT,
        user=settings.DB_USER,
        password=settings.DB_PASSWORD,
        database=settings.DB_NAME
    )
    cursor = conn.cursor()
    
    cursor.execute("SHOW COLUMNS FROM instructions LIKE 'description'")
    if not cursor.fetchone():
        cursor.execute("ALTER TABLE instructions ADD COLUMN description TEXT")
        logger.info("Добавлено поле description в instructions")
    
    cursor.execute("SHOW COLUMNS FROM instructions LIKE 'external_url'")
    if cursor.fetchone():
        cursor.execute("ALTER TABLE instructions DROP COLUMN external_url")
        logger.info("Удалено external_url")
    
    cursor.execute("SHOW COLUMNS FROM instructions LIKE 'part_category_id'")
    if cursor.fetchone():
        cursor.execute("ALTER TABLE instructions DROP COLUMN part_category_id")
        logger.info("Удалено part_category_id")
    
    try:
        cursor.execute("ALTER TABLE part_links ADD UNIQUE KEY unique_part_car_url (part_id, car_id, url)")
        logger.info("Добавлен уникальный ключ в part_links")
    except mysql.connector.Error as e:
        if e.errno == 1061:  
            logger.info("Уникальный ключ unique_part_car_url уже существует")
        else:
            raise
    
    try:
       cursor.execute("ALTER TABLE cars ADD UNIQUE KEY unique_car (brand, model, generation)")
       logger.info("Добавлен уникальный ключ в cars")
    except mysql.connector.Error as e:
        if e.errno == 1061:
            logger.info("Уникальный ключ unique_car уже существует")
        else:
            raise

    try:
        cursor.execute("CREATE INDEX idx_parts_name ON parts(name)")
        logger.info("Индекс idx_parts_name создан")
    except mysql.connector.Error as e:
        if e.errno == 1061:
            logger.info("Индекс idx_parts_name уже существует")
        else:
            raise

    try:
        cursor.execute("CREATE INDEX idx_cars_brand ON cars(brand)")
        logger.info("Индекс idx_cars_brand создан")
    except mysql.connector.Error as e:
        if e.errno == 1061:
            logger.info("Индекс idx_cars_brand уже существует")
        else:
            raise

    try:
        cursor.execute("CREATE INDEX idx_cars_model ON cars(model)")
        logger.info("Индекс idx_cars_model создан")
    except mysql.connector.Error as e:
        if e.errno == 1061:
            logger.info("Индекс idx_cars_model уже существует")
        else:
            raise

    conn.commit()
    cursor.close()
    conn.close()
    logger.info("Миграция завершена")

if __name__ == "__main__":
    run_migration()