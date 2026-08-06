import pytest
from app.repositories import part_repo

@pytest.mark.skip(reason="Требуется запущенный MySQL и фикстура test_db")
def test_get_all_parts_with_links(test_db):
    from app.database import get_db_connection
    original_get = get_db_connection
    def fake_get():
        conn = mysql.connector.connect(
            host=test_db['host'],
            user=test_db['user'],
            password=test_db['password'],
            database=test_db['database']
        )
        return conn
    import app.repositories.part_repo
    app.repositories.part_repo.get_db_connection = fake_get
    
    parts = part_repo.get_all_parts_with_links()
    assert len(parts) >= 1
    assert parts[0]['part_name'] == 'Тестовая деталь'
    assert parts[0]['car_name'] == 'Test Car 1'
    assert parts[0]['category'] == 'Тестовая категория'