import pytest
from app.services.price_updater import update_prices_batch

def test_update_prices_batch(mocker):
    mock_parse = mocker.patch('app.services.price_updater.parse_price')
    mock_parse.side_effect = [1000.0, None, 30.0]  

    mock_conn = mocker.MagicMock()
    mock_cursor = mocker.MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    
    mock_cursor.fetchall.return_value = [
        (1, 'https://example.com/1'),
        (2, 'https://example.com/2'),
        (3, 'https://example.com/3'),
    ]
    
    mocker.patch('app.services.price_updater.get_db_connection', return_value=mock_conn)

    updated = update_prices_batch(interval_hours=0)

    assert updated == 1  

    mock_conn.commit.assert_called_once()
    
    calls = mock_cursor.execute.call_args_list
    update_calls = calls[1:]  
    
    assert len(update_calls) == 3

    first_update_sql, first_params = update_calls[0][0]  
    assert 'parsed_price = %s' in first_update_sql
    assert first_params[0] == 1000.0  

    second_update_sql, second_params = update_calls[1][0]
    assert 'parsed_price' not in second_update_sql 
    assert len(second_params) == 1  
    third_update_sql, third_params = update_calls[2][0]
    assert len(third_params) == 1