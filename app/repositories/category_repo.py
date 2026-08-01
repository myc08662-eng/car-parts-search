from app.database import get_db_connection

def get_all_categories():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT id, name FROM categories ORDER BY name")
    categories = cursor.fetchall()
    cursor.close()
    conn.close()
    return categories