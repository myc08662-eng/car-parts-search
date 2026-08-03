from app.database import get_db_connection
from app.services.price_parser import parse_price
import logging
from datetime import datetime, timedelta
from app.config import get_settings

settings = get_settings()
logger = logging.getLogger(__name__)

def update_prices_batch(interval_hours: int = 6):
    """
    Обновляет парсенные цены для ссылок, у которых обновление старше interval_hours.
    Возвращает количество успешно обновлённых цен.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    threshold = datetime.now() - timedelta(hours=interval_hours)
    cursor.execute("""
        SELECT id, url FROM part_links
        WHERE is_active = 1
          AND (price_updated_at IS NULL OR price_updated_at < %s)
        LIMIT 100
    """, (threshold,))
    rows = cursor.fetchall()
    logger.info(f"Обновление цен для {len(rows)} ссылок")

    updated = 0
    skipped = 0
    for link_id, url in rows:
        new_price = parse_price(url)
        
        if new_price is not None and new_price >= settings.MIN_REAL_PRICE:
            cursor.execute(
                "UPDATE part_links SET parsed_price = %s, price_updated_at = NOW() WHERE id = %s",
                (new_price, link_id)
            )
            updated += 1
        else:
            skipped += 1
            cursor.execute(
                "UPDATE part_links SET price_updated_at = NOW() WHERE id = %s",
                (link_id,)
            )
    
    conn.commit()
    logger.info(f"Обновлено цен: {updated}, пропущено (меньше порога или None): {skipped}")
    cursor.close()
    conn.close()
    return updated