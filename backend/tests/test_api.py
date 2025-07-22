import json
import os

import pytest
from app import app, get_db_connection, init_db

# Test database configuration
TEST_DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'https://db.assets.orb.local/'),
    'database': os.getenv('DB_NAME', 'logs_db'),
    'user': os.getenv('DB_USER', 'logs_user'),
    'password': os.getenv('DB_PASSWORD', 'logs_password'),
    'port': os.getenv('DB_PORT', 5432)
}

@pytest.fixture(scope='session')
def test_db():
    """Create test database and tables"""
    # Override the database configuration for testing
    app.config['DB_CONFIG'] = TEST_DB_CONFIG
    
    # Initialize the test database
    init_db()
    
    yield
    
    # Cleanup after all tests
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM logs')  # Clear logs instead of dropping table
    conn.commit()
    cursor.close()
    conn.close()

@pytest.fixture
def client(test_db):
    """Create a test client"""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_health_endpoint(client):
    """Test the health endpoint"""
    response = client.get('/health')
    print(response.data)
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'status' in data
    assert 'database' in data
    assert 'timestamp' in data

def test_add_log(client):
    """Test adding a new log"""
    test_log = {
        'level': 'info',
        'message': 'Test log message',
        'service': 'test_service',
        'data': {'key': 'value'}
    }
    
    response = client.post('/logs',
                          data=json.dumps(test_log),
                          content_type='application/json')
    
    assert response.status_code == 201
    data = json.loads(response.data)
    assert data['success'] is True
    assert 'log' in data
    assert data['log']['message'] == test_log['message']
    assert data['log']['level'] == test_log['level']
    assert data['log']['service'] == test_log['service']

def test_get_logs(client):
    """Test retrieving logs"""
    # First add a test log
    test_log = {
        'level': 'info',
        'message': 'Test log for retrieval',
        'service': 'test_service'
    }
    client.post('/logs',
                data=json.dumps(test_log),
                content_type='application/json')
    
    # Test getting logs
    response = client.get('/logs')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'logs' in data
    assert 'total' in data
    assert 'returned' in data
    assert 'limit' in data
    assert 'offset' in data
    
    # Test pagination
    response = client.get('/logs?limit=1&offset=0')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert len(data['logs']) <= 1

def test_get_stats(client):
    """Test getting statistics"""
    # Add some test logs first
    test_logs = [
        {'level': 'info', 'message': 'Test log 1', 'service': 'service1'},
        {'level': 'error', 'message': 'Test log 2', 'service': 'service2'},
        {'level': 'warning', 'message': 'Test log 3', 'service': 'service1'}
    ]
    
    for log in test_logs:
        client.post('/logs',
                   data=json.dumps(log),
                   content_type='application/json')
    
    response = client.get('/stats')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'total_logs' in data
    assert 'levels' in data
    assert 'services' in data
    assert 'last_log' in data
    
    # Verify the stats contain our test data
    assert data['total_logs'] >= len(test_logs)
    assert 'info' in data['levels']
    assert 'error' in data['levels']
    assert 'warning' in data['levels']
    assert 'service1' in data['services']
    assert 'service2' in data['services']

def test_clear_logs(client):
    """Test clearing all logs"""
    # First add a test log
    test_log = {
        'level': 'info',
        'message': 'Test log to be cleared',
        'service': 'test_service'
    }
    client.post('/logs',
                data=json.dumps(test_log),
                content_type='application/json')
    
    # Clear logs
    response = client.delete('/logs/clear')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'success' in data
    assert data['success'] is True

    # Verify logs are cleared
    response = client.get('/logs')
    data = json.loads(response.data)
    assert data['total'] == 0

def test_invalid_log_data(client):
    """Test adding invalid log data"""
    invalid_log = {
        'invalid_field': 'test'
    }
    
    response = client.post('/logs',
                          data=json.dumps(invalid_log),
                          content_type='application/json')
    
    assert response.status_code == 201  # Should still work as we have defaults
    data = json.loads(response.data)
    assert data['success'] is True
    assert data['log']['level'] == 'info'  # Default value
    assert data['log']['message'] == ''  # Default value
    assert data['log']['service'] == 'unknown'  # Default value
