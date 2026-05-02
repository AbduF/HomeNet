"""Security & Functionality Tests for HomeNet 2026"""
import pytest
from app import app, db_query
import sqlite3

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_sql_injection_protection(client):
    """Verify parameterized queries prevent SQL injection"""
    # Attempt injection via API
    response = client.get('/api/hosts?page=1;DROP TABLE hosts--', 
                         headers={'Authorization': 'Basic YWRtaW46MTIzNDU2'})
    # Should return error or empty, NOT execute injection
    assert response.status_code in [200, 400]
    
    # Verify hosts table still exists
    conn = sqlite3.connect('homenet.db')
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='hosts'")
    assert cursor.fetchone() is not None
    conn.close()

def test_csrf_protection(client):
    """Verify CSRF token required for state-changing requests"""
    # POST without CSRF token should fail
    response = client.post('/api/setup', json={})
    assert response.status_code == 403  # CSRF token missing

def test_rate_limiting(client):
    """Verify rate limiting on login endpoint"""
    # Make 6 rapid login attempts
    for _ in range(6):
        response = client.post('/login', data={
            'username': 'admin',
            'password': 'wrongpass'
        })
    
    # 6th attempt should be rate limited
    assert response.status_code == 429 or 'locked' in response.get_data(as_text=True).lower()

def test_password_policy(client):
    """Verify password complexity enforcement"""
    with app.app_context():
        from app import validate_password
        
        # Test weak passwords
        assert validate_password("short")[0] == False
        assert validate_password("nouppercase1!")[0] == False
        assert validate_password("NOLOWERCASE1!")[0] == False
        assert validate_password("NoSpecial1")[0] == False
        
        # Test strong password
        valid, msg = validate_password("SecureP@ss123")
        assert valid == True
        assert msg is None

def test_health_endpoint(client):
    """Verify health check returns proper structure"""
    response = client.get('/health')
    data = response.get_json()
    
    assert response.status_code == 200
    assert 'status' in data
    assert 'timestamp' in data
    assert data['status'] in ['healthy', 'degraded']