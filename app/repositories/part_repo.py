from app.database import get_db_connection

def get_all_parts_with_links():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT 
            p.id as part_id,
            c.id as car_id,
            p.name AS part_name,
            cat.name as category,
            pl.price as original_price,
            pl.parsed_price,
            pl.price_updated_at,
            pl.url,
            pl.vendor,
            CONCAT(c.brand, ' ', c.model, IFNULL(CONCAT(' ', c.generation), '')) AS car_name
        FROM part_links pl
        JOIN parts p ON pl.part_id = p.id
        JOIN cars c ON pl.car_id = c.id
        JOIN categories cat ON p.category_id = cat.id
        WHERE pl.is_active = 1
    """)
    parts = cursor.fetchall()
    cursor.close()
    conn.close()
    return parts

def search_by_sql_like(query: str, limit: int = 20):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    search_term = f"%{query}%"
    cursor.execute("""
        SELECT 
            p.id as part_id,
            c.id as car_id,
            p.name AS part_name,
            cat.name as category,
            pl.price as original_price,
            pl.parsed_price,
            pl.price_updated_at,
            pl.url,
            pl.vendor,
            CONCAT(c.brand, ' ', c.model, IFNULL(CONCAT(' ', c.generation), '')) AS car_name
        FROM part_links pl
        JOIN parts p ON pl.part_id = p.id
        JOIN cars c ON pl.car_id = c.id
        JOIN categories cat ON p.category_id = cat.id
        WHERE (LOWER(p.name) LIKE LOWER(%s) 
           OR LOWER(c.brand) LIKE LOWER(%s) 
           OR LOWER(c.model) LIKE LOWER(%s))
          AND pl.is_active = 1
        LIMIT %s
    """, (search_term, search_term, search_term, limit))
    results = cursor.fetchall()
    cursor.close()
    conn.close()
    return results