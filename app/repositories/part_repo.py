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

def search_by_sql_like(query: str, category: str = None, offset: int = None, limit: int = None):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    search_term = f"%{query}%"
    sql = """
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
    """
    params = [search_term, search_term, search_term]
    if category:
        sql += " AND LOWER(cat.name) = LOWER(%s)"
        params.append(category)
    if offset is not None and limit is not None:
        sql += " LIMIT %s OFFSET %s"
        params.append(limit)
        params.append(offset)
    elif limit is not None:
        sql += " LIMIT %s"
        params.append(limit)
    cursor.execute(sql, params)
    results = cursor.fetchall()
    cursor.close()
    conn.close()
    return results

def count_search_results(query: str, category: str = None):
    conn = get_db_connection()
    cursor = conn.cursor()
    search_term = f"%{query}%"
    sql = """
        SELECT COUNT(*) FROM part_links pl
        JOIN parts p ON pl.part_id = p.id
        JOIN cars c ON pl.car_id = c.id
        JOIN categories cat ON p.category_id = cat.id
        WHERE (LOWER(p.name) LIKE LOWER(%s) 
           OR LOWER(c.brand) LIKE LOWER(%s) 
           OR LOWER(c.model) LIKE LOWER(%s))
          AND pl.is_active = 1
    """
    params = [search_term, search_term, search_term]
    if category:
        sql += " AND LOWER(cat.name) = LOWER(%s)"
        params.append(category)
    cursor.execute(sql, params)
    total = cursor.fetchone()[0]
    cursor.close()
    conn.close()
    return total