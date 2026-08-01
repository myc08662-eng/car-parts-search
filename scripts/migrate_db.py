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
        if "Duplicate entry" in str(e):
            logger.warning("Уникальный ключ уже существует или есть дубли – пропускаем")
        else:
            raise
    
    try:
        cursor.execute("ALTER TABLE cars ADD UNIQUE KEY unique_car (brand, model, generation)")
        logger.info("Добавлен уникальный ключ в cars")
    except Exception as e:
        logger.warning(f"Не удалось добавить уникальность cars: {e}")
    
    conn.commit()
    cursor.close()
    conn.close()
    logger.info("Миграция завершена")

if __name__ == "__main__":
    run_migration()