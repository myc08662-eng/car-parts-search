import pytest
from unittest.mock import MagicMock, patch
from app.repositories import part_repo

def test_get_all_parts_with_links():
    """Тест проверяет, что get_all_parts_with_links возвращает правильные данные"""
    mock_cursor = MagicMock()
    mock_cursor.fetchall.return_value = [
        {
            'part_id': 1,
            'car_id': 1,
            'part_name': 'Тестовая деталь',
            'category': 'Тестовая категория',
            'original_price': 1000.0,
            'parsed_price': None,
            'price_updated_at': None,
            'url': 'https://example.com',
            'vendor': 'TestVendor',
            'car_name': 'Test Car 1'
        }
    ]

    mock_conn = MagicMock()
    mock_conn.cursor.return_value = mock_cursor

    with patch('app.repositories.part_repo.get_db_connection', return_value=mock_conn):
        parts = part_repo.get_all_parts_with_links()
    assert len(parts) == 1
    assert parts[0]['part_name'] == 'Тестовая деталь'
    assert parts[0]['car_name'] == 'Test Car 1'
    assert parts[0]['category'] == 'Тестовая категория'
    assert parts[0]['vendor'] == 'TestVendor'
    assert parts[0]['original_price'] == 1000.0

    mock_cursor.execute.assert_called_once()
    mock_cursor.close.assert_called_once()
    mock_conn.close.assert_called_once()