import mysql.connector
from mysql.connector import Error
from app.config import get_settings

settings = get_settings()

def get_db_connection():
    try:
        conn = mysql.connector.connect(
            host=settings.DB_HOST,
            port=settings.DB_PORT,
            user=settings.DB_USER,
            password=settings.DB_PASSWORD,
            database=settings.DB_NAME
        )
        return conn
    except Error as e:
        raise RuntimeError(f"Database connection failed: {e}")