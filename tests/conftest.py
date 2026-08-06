import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database import get_db_connection
from app.services.tfidf_search import TFIDFSearch
from app.services import search_service
import mysql.connector
import os

@pytest.fixture
def client():
    return TestClient(app)

@pytest.fixture
def mock_db_connection(mocker):
    mock_conn = mocker.MagicMock()
    mock_cursor = mocker.MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    mocker.patch('app.repositories.category_repo.get_db_connection', return_value=mock_conn)
    return mock_conn, mock_cursor

@pytest.fixture
def mock_search_engine(mocker):
    mock_engine = mocker.MagicMock(spec=TFIDFSearch)
    mock_engine.is_fitted = True
    mock_engine.search_by_category.return_value = [
        {
            "part_id": 1,
            "car_id": 1,
            "part_name": "Масляный фильтр",
            "car_name": "Toyota Corolla E150",
            "category": "Фильтры",
            "price": 650,
            "original_price": 650,
            "parsed_price": None,
            "url": "https://example.com",
            "vendor": "Ozon",
            "similarity": 0.9
        }
    ]
    mocker.patch('app.services.search_service.search_engine', mock_engine)
    return mock_engine

@pytest.fixture(scope='session')
def test_db():
    conn = mysql.connector.connect(
        host='localhost',
        user='root',
        password='',
        database=''
    )
    cursor = conn.cursor()
    cursor.execute("DROP DATABASE IF EXISTS test_car_parts_db")
    cursor.execute("CREATE DATABASE test_car_parts_db")
    cursor.close()
    conn.close()

    conn = mysql.connector.connect(
        host='localhost',
        user='root',
        password='',
        database='test_car_parts_db'
    )
    cursor = conn.cursor()
    schema_path = os.path.join(os.path.dirname(__file__), '..', 'schema.sql')
    with open(schema_path, 'r', encoding='utf-8') as f:
        sql = f.read()
        for statement in sql.split(';'):
            if statement.strip():
                cursor.execute(statement)
    conn.commit()
    cursor.close()
    conn.close()

    conn = mysql.connector.connect(
        host='localhost',
        user='root',
        password='',
        database='test_car_parts_db'
    )
    cursor = conn.cursor()
    cursor.execute("INSERT INTO cars (brand, model, generation) VALUES ('Test', 'Car', '1')")
    cursor.execute("INSERT INTO categories (name) VALUES ('Тестовая категория')")
    cursor.execute("INSERT INTO parts (name, category_id) VALUES ('Тестовая деталь', 1)")
    cursor.execute("INSERT INTO part_links (part_id, car_id, url, price, vendor) VALUES (1, 1, 'https://example.com', 1000, 'TestVendor')")
    conn.commit()
    cursor.close()
    conn.close()

    yield {
        'host': 'localhost',
        'user': 'root',
        'password': '',
        'database': 'test_car_parts_db'
    }

    conn = mysql.connector.connect(
        host='localhost',
        user='root',
        password='',
        database=''
    )
    cursor = conn.cursor()
    cursor.execute("DROP DATABASE IF EXISTS test_car_parts_db")
    cursor.close()
    conn.close()