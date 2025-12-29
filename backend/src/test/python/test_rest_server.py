"""
Unit tests for REST server.
Tests individual functions and endpoints.
"""
import sys
import os
import pytest
import json

# Add the PythonScripts directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../main/PythonScripts'))

from rest_server import app, db, query, LoadDB, update_tinydb, SWITCH_MAIN_MAP

@pytest.fixture
def client():
    """Create a test client for the Flask app."""
    app.config['TESTING'] = True
    with app.test_client() as client:
        with app.app_context():
            # Reset database for each test
            db.truncate()
            LoadDB()
        yield client

def test_health_check(client):
    """Test the health check endpoint."""
    response = client.get('/health')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['status'] == 'healthy'
    assert data['db_count'] == 80

def test_database_initialization():
    """Test that database initializes with correct number of records."""
    db.truncate()
    LoadDB()
    assert len(db) == 80
    
    # Verify some sample records
    record1 = db.search(query.INDEX == 1)
    assert len(record1) == 1
    assert record1[0]['TAG'] == 'HMI_RHT'
    assert record1[0]['HMI_VALUEi'] == 25
    
    record50 = db.search(query.INDEX == 50)
    assert len(record50) == 1
    assert record50[0]['TAG'] == 'RR1ABspeed_HMI'

def test_update_tinydb_single_record():
    """Test updating a single database record."""
    db.truncate()
    LoadDB()
    
    # Update a record
    update_data = {
        "INDEX": 1,
        "TAG": "HMI_RHT",
        "HMI_VALUEi": 30,
        "HMI_VALUEb": True,
        "PI_VALUEf": 1.0,
        "PI_VALUEb": False,
        "HMI_READi": 2
    }
    
    updated_indexes = update_tinydb(update_data)
    assert len(updated_indexes) == 1
    assert updated_indexes[0] == 1
    
    # Verify the update
    record = db.search(query.INDEX == 1)
    assert record[0]['HMI_VALUEi'] == 30
    assert record[0]['HMI_VALUEb'] == True
    assert record[0]['HMI_READi'] == 2

def test_update_tinydb_multiple_records():
    """Test updating multiple database records."""
    db.truncate()
    LoadDB()
    
    # Update multiple records
    update_data = [
        {"INDEX": 1, "TAG": "HMI_RHT", "HMI_VALUEi": 35, "HMI_VALUEb": False, "PI_VALUEf": 0.0, "PI_VALUEb": True, "HMI_READi": 2},
        {"INDEX": 2, "TAG": "HMI_TramStopTime", "HMI_VALUEi": 15, "HMI_VALUEb": False, "PI_VALUEf": 0.0, "PI_VALUEb": True, "HMI_READi": 2}
    ]
    
    updated_indexes = update_tinydb(update_data)
    assert len(updated_indexes) == 2
    assert 1 in updated_indexes
    assert 2 in updated_indexes
    
    # Verify the updates
    record1 = db.search(query.INDEX == 1)
    assert record1[0]['HMI_VALUEi'] == 35
    
    record2 = db.search(query.INDEX == 2)
    assert record2[0]['HMI_VALUEi'] == 15

def test_update_tinydb_switch_mirroring():
    """Test that switch updates are mirrored to main feedback tags."""
    db.truncate()
    LoadDB()
    
    # Update a switch command tag
    update_data = {
        "INDEX": 11,
        "TAG": "HMI_Switch1ABb",
        "HMI_VALUEi": 0,
        "HMI_VALUEb": False,
        "PI_VALUEf": 0.0,
        "PI_VALUEb": True,
        "HMI_READi": 2
    }
    
    update_tinydb(update_data)
    
    # Verify the main feedback tag was updated
    main_record = db.search(query.TAG == "Switch1Main_HMIb")
    assert len(main_record) == 1
    assert main_record[0]['PI_VALUEb'] == False  # Should mirror the HMI_VALUEb
    assert main_record[0]['HMI_READi'] == 1  # Should be marked as PI-origin update

def test_hmi_check_updates_with_updates(client):
    """Test HMI check updates endpoint when updates are available."""
    # Mark some records with HMI_READi = 1
    db.update({"HMI_READi": 1}, query.INDEX == 1)
    db.update({"HMI_READi": 1}, query.INDEX == 2)
    
    response = client.get('/api/hmi/check-updates')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['has_updates'] == True
    assert data['count'] == 2

def test_hmi_check_updates_without_updates(client):
    """Test HMI check updates endpoint when no updates are available."""
    response = client.get('/api/hmi/check-updates')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['has_updates'] == False
    assert data['count'] == 0

def test_hmi_get_updates(client):
    """Test HMI get updates endpoint."""
    # Mark some records with HMI_READi = 1
    db.update({"HMI_READi": 1}, query.INDEX == 1)
    db.update({"HMI_READi": 1}, query.INDEX == 2)
    
    response = client.get('/api/hmi/get-updates')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert len(data) == 2
    
    # Verify flags were cleared
    remaining = db.count(query.HMI_READi == 1)
    assert remaining == 0

def test_hmi_send_updates(client):
    """Test HMI send updates endpoint."""
    update_data = [{
        "INDEX": 1,
        "TAG": "HMI_RHT",
        "HMI_VALUEi": 40,
        "HMI_VALUEb": True,
        "PI_VALUEf": 0.0,
        "PI_VALUEb": True
    }]
    
    response = client.post('/api/hmi/send-updates',
                          data=json.dumps(update_data),
                          content_type='application/json')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['success'] == True
    assert data['updated_count'] == 1
    
    # Verify the update
    record = db.search(query.INDEX == 1)
    assert record[0]['HMI_VALUEi'] == 40
    assert record[0]['HMI_READi'] == 2  # Should default to 2 for HMI-origin

def test_hmi_get_all(client):
    """Test HMI get all records endpoint."""
    response = client.get('/api/hmi/get-all')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert len(data) == 80
    assert data[0]['INDEX'] == 1

def test_pi_check_updates_with_updates(client):
    """Test PI check updates endpoint when updates are available."""
    # Mark some records with HMI_READi = 2
    db.update({"HMI_READi": 2}, query.INDEX == 1)
    
    response = client.get('/api/pi/check-updates')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['has_updates'] == True
    assert data['count'] == 1

def test_pi_get_updates(client):
    """Test PI get updates endpoint."""
    # Mark some records with HMI_READi = 2
    db.update({"HMI_READi": 2}, query.INDEX == 1)
    db.update({"HMI_READi": 2}, query.INDEX == 2)
    
    response = client.get('/api/pi/get-updates')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert len(data) == 2
    
    # Verify flags were cleared
    remaining = db.count(query.HMI_READi == 2)
    assert remaining == 0

def test_pi_send_updates(client):
    """Test PI send updates endpoint."""
    update_data = [{
        "INDEX": 50,
        "TAG": "RR1ABspeed_HMI",
        "HMI_VALUEi": 0,
        "HMI_VALUEb": True,
        "PI_VALUEf": 0.25,
        "PI_VALUEb": True,
        "HMI_READi": 1
    }]
    
    response = client.post('/api/pi/send-updates',
                          data=json.dumps(update_data),
                          content_type='application/json')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['success'] == True
    assert data['updated_count'] == 1
    
    # Verify the update
    record = db.search(query.INDEX == 50)
    assert record[0]['PI_VALUEf'] == 0.25
    assert record[0]['HMI_READi'] == 1

def test_debug_print_db(client):
    """Test debug print database endpoint."""
    response = client.get('/api/debug/print-db')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert len(data) == 80

def test_send_updates_empty_dict(client):
    """Test send updates with empty dict."""
    response = client.post('/api/hmi/send-updates',
                          data=json.dumps({}),
                          content_type='application/json')
    # Empty dict is valid, returns success with 0 updates
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['success'] == True
    assert data['updated_count'] == 0

def test_send_updates_empty_list(client):
    """Test send updates with empty list."""
    response = client.post('/api/hmi/send-updates',
                          data=json.dumps([]),
                          content_type='application/json')
    # Empty list is valid, returns success with 0 updates
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['success'] == True
    assert data['updated_count'] == 0
