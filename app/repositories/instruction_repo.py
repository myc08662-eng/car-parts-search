from app.database import get_db_connection

def get_instructions_by_car(car_id: int):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT id, title, description, file_path
        FROM instructions
        WHERE car_id = %s
    """, (car_id,))
    instructions = cursor.fetchall()
    cursor.close()
    conn.close()
    return instructions

def get_car_by_id(car_id: int):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT brand, model, generation FROM cars WHERE id = %s", (car_id,))
    car = cursor.fetchone()
    cursor.close()
    conn.close()
    return car