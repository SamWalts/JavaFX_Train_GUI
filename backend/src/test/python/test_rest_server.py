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

from rest_server import app, db, query, LoadDB, update_tinydb, SWITCH_MAIN_MAP, db_lock

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
    print(f"Response data: {response.data}")
    print(f"Parsed data type: {type(data)}")
    print(f"Parsed data: {data}")

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

def test_multiple_post_operations_on_db(client):
    """Test multiple POST operations on the database."""
    # First update
    update_data1 = [{
        "INDEX": 5,
        "TAG": "HMI_TestTag1",
        "HMI_VALUEi": 10,
        "HMI_VALUEb": True,
        "PI_VALUEf": 0.5,
        "PI_VALUEb": True
    }]

    response1 = client.post('/api/hmi/send-updates',
                           data=json.dumps(update_data1),
                           content_type='application/json')
    assert response1.status_code == 200
    data1 = json.loads(response1.data)
    assert data1['success'] == True
    assert data1['updated_count'] == 1

    # Second update
    update_data2 = [{
        "INDEX": 10,
        "TAG": "HMI_TestTag2",
        "HMI_VALUEi": 20,
        "HMI_VALUEb": False,
        "PI_VALUEf": 1.5,
        "PI_VALUEb": False
    }]
    response2 = client.post('/api/hmi/send-updates',
                           data=json.dumps(update_data2),
                           content_type='application/json')
    assert response2.status_code == 200
    data2 = json.loads(response2.data)
    assert data2['success'] == True
    assert data2['updated_count'] == 1

    # Verify both updates
    record1 = db.search(query.INDEX == 5)
    assert record1[0]['HMI_VALUEi'] == 10

    record2 = db.search(query.INDEX == 10)
    assert record2[0]['HMI_VALUEi'] == 20


def test_100_iterations_hmi_send_updates(client):
    """Test 100 iterations of HMI send updates endpoint."""
    for i in range(100):
        update_data = [{
            "INDEX": 1,
            "TAG": "HMI_RHT",
            "HMI_VALUEi": i,
            "HMI_VALUEb": i % 2 == 0,
            "PI_VALUEf": float(i) / 10.0,
            "PI_VALUEb": i % 2 == 1
        }]

        response = client.post('/api/hmi/send-updates',
                              data=json.dumps(update_data),
                              content_type='application/json')
        assert response.status_code == 200, f"Iteration {i}: POST failed with status {response.status_code}"
        data = json.loads(response.data)
        assert data['success'] == True, f"Iteration {i}: success=False"
        assert data['updated_count'] == 1, f"Iteration {i}: updated_count != 1"

        # Verify the update
        with db_lock:
            record = db.search(query.INDEX == 1)
            assert record[0]['HMI_VALUEi'] == i, f"Iteration {i}: HMI_VALUEi mismatch"

    print("Successfully completed 100 iterations of HMI send updates")


def test_100_iterations_pi_send_updates(client):
    """Test 100 iterations of PI send updates endpoint."""
    for i in range(100):
        update_data = [{
            "INDEX": 50,
            "TAG": "RR1ABspeed_HMI",
            "HMI_VALUEi": i,
            "HMI_VALUEb": True,
            "PI_VALUEf": float(i) / 100.0,
            "PI_VALUEb": i % 2 == 0,
            "HMI_READi": 1
        }]

        response = client.post('/api/pi/send-updates',
                              data=json.dumps(update_data),
                              content_type='application/json')
        assert response.status_code == 200, f"Iteration {i}: POST failed with status {response.status_code}"
        data = json.loads(response.data)
        assert data['success'] == True, f"Iteration {i}: success=False"
        assert data['updated_count'] == 1, f"Iteration {i}: updated_count != 1"

        # Verify the update
        with db_lock:
            record = db.search(query.INDEX == 50)
            assert record[0]['PI_VALUEf'] == float(i) / 100.0, f"Iteration {i}: PI_VALUEf mismatch"

    print("Successfully completed 100 iterations of PI send updates")


def test_100_iterations_hmi_get_all(client):
    """Test 100 iterations of HMI get all endpoint."""
    for i in range(100):
        response = client.get('/api/hmi/get-all')
        assert response.status_code == 200, f"Iteration {i}: GET failed with status {response.status_code}"
        data = json.loads(response.data)
        assert len(data) == 80, f"Iteration {i}: Expected 80 records, got {len(data)}"

    print("Successfully completed 100 iterations of HMI get all")


def test_100_iterations_pi_get_all(client):
    """Test 100 iterations of PI get all endpoint."""
    for i in range(100):
        response = client.get('/api/pi/get-all')
        assert response.status_code == 200, f"Iteration {i}: GET failed with status {response.status_code}"
        data = json.loads(response.data)
        assert len(data) == 80, f"Iteration {i}: Expected 80 records, got {len(data)}"

    print("Successfully completed 100 iterations of PI get all")


def test_100_iterations_hmi_check_updates(client):
    """Test 100 iterations of HMI check updates endpoint."""
    for i in range(100):
        # Set up some updates on even iterations
        if i % 2 == 0:
            with db_lock:
                db.update({"HMI_READi": 1}, query.INDEX == 1)

        response = client.get('/api/hmi/check-updates')
        assert response.status_code == 200, f"Iteration {i}: GET failed with status {response.status_code}"
        data = json.loads(response.data)
        assert 'has_updates' in data, f"Iteration {i}: Missing 'has_updates' key"
        assert 'count' in data, f"Iteration {i}: Missing 'count' key"

        # Reset for next iteration
        with db_lock:
            db.update({"HMI_READi": 0}, query.INDEX == 1)

    print("Successfully completed 100 iterations of HMI check updates")


def test_100_iterations_pi_check_updates(client):
    """Test 100 iterations of PI check updates endpoint."""
    for i in range(100):
        # Set up some updates on even iterations
        if i % 2 == 0:
            with db_lock:
                db.update({"HMI_READi": 2}, query.INDEX == 1)

        response = client.get('/api/pi/check-updates')
        assert response.status_code == 200, f"Iteration {i}: GET failed with status {response.status_code}"
        data = json.loads(response.data)
        assert 'has_updates' in data, f"Iteration {i}: Missing 'has_updates' key"
        assert 'count' in data, f"Iteration {i}: Missing 'count' key"

        # Reset for next iteration
        with db_lock:
            db.update({"HMI_READi": 0}, query.INDEX == 1)

    print("Successfully completed 100 iterations of PI check updates")


def test_100_iterations_hmi_get_updates(client):
    """Test 100 iterations of HMI get updates endpoint."""
    for i in range(100):
        # Set up updates before getting them
        with db_lock:
            db.update({"HMI_READi": 1}, query.INDEX == (i % 10) + 1)

        response = client.get('/api/hmi/get-updates')
        assert response.status_code == 200, f"Iteration {i}: GET failed with status {response.status_code}"
        data = json.loads(response.data)
        assert isinstance(data, list), f"Iteration {i}: Expected list response"

        # Verify flags were cleared
        with db_lock:
            remaining = db.count(query.HMI_READi == 1)
            assert remaining == 0, f"Iteration {i}: HMI_READi flags not cleared"

    print("Successfully completed 100 iterations of HMI get updates")


def test_100_iterations_pi_get_updates(client):
    """Test 100 iterations of PI get updates endpoint."""
    for i in range(100):
        # Set up updates before getting them
        with db_lock:
            db.update({"HMI_READi": 2}, query.INDEX == (i % 10) + 1)

        response = client.get('/api/pi/get-updates')
        assert response.status_code == 200, f"Iteration {i}: GET failed with status {response.status_code}"
        data = json.loads(response.data)
        assert isinstance(data, list), f"Iteration {i}: Expected list response"

        # Verify flags were cleared
        with db_lock:
            remaining = db.count(query.HMI_READi == 2)
            assert remaining == 0, f"Iteration {i}: HMI_READi flags not cleared"

    print("Successfully completed 100 iterations of PI get updates")


def test_100_iterations_health_check(client):
    """Test 100 iterations of health check endpoint."""
    for i in range(100):
        response = client.get('/health')
        assert response.status_code == 200, f"Iteration {i}: GET failed with status {response.status_code}"
        data = json.loads(response.data)
        assert data['status'] == 'healthy', f"Iteration {i}: status != 'healthy'"
        assert data['db_count'] == 80, f"Iteration {i}: db_count != 80"

    print("Successfully completed 100 iterations of health check")


def test_100_iterations_debug_print_db(client):
    """Test 100 iterations of debug print db endpoint."""
    for i in range(100):
        response = client.get('/api/debug/print-db')
        assert response.status_code == 200, f"Iteration {i}: GET failed with status {response.status_code}"
        data = json.loads(response.data)
        assert len(data) == 80, f"Iteration {i}: Expected 80 records, got {len(data)}"

    print("Successfully completed 100 iterations of debug print db")


def test_100_iterations_mixed_operations(client):
    """Test 100 iterations of mixed GET and POST operations."""
    for i in range(100):
        # POST HMI update
        update_data = [{
            "INDEX": (i % 10) + 1,
            "TAG": f"HMI_Test_{i}",
            "HMI_VALUEi": i,
            "HMI_VALUEb": i % 2 == 0,
            "PI_VALUEf": float(i) / 10.0,
            "PI_VALUEb": i % 2 == 1
        }]
        response = client.post('/api/hmi/send-updates',
                              data=json.dumps(update_data),
                              content_type='application/json')
        assert response.status_code == 200, f"Iteration {i}: HMI POST failed"

        # GET all
        response = client.get('/api/hmi/get-all')
        assert response.status_code == 200, f"Iteration {i}: GET all failed"

        # POST PI update
        pi_data = [{
            "INDEX": (i % 10) + 50,
            "TAG": f"PI_Test_{i}",
            "HMI_VALUEi": 0,
            "HMI_VALUEb": True,
            "PI_VALUEf": float(i) / 100.0,
            "PI_VALUEb": i % 2 == 0,
            "HMI_READi": 1
        }]
        response = client.post('/api/pi/send-updates',
                              data=json.dumps(pi_data),
                              content_type='application/json')
        assert response.status_code == 200, f"Iteration {i}: PI POST failed"

        # Check updates
        response = client.get('/api/hmi/check-updates')
        assert response.status_code == 200, f"Iteration {i}: HMI check updates failed"

        response = client.get('/api/pi/check-updates')
        assert response.status_code == 200, f"Iteration {i}: PI check updates failed"

        # Health check
        response = client.get('/health')
        assert response.status_code == 200, f"Iteration {i}: Health check failed"

    print("Successfully completed 100 iterations of mixed operations")


def test_100_iterations_batch_updates(client):
    """Test 100 iterations of batch updates with multiple records each."""
    for i in range(100):
        # Update 5 records at once
        update_data = [
            {"INDEX": 1, "TAG": "HMI_RHT", "HMI_VALUEi": i, "HMI_VALUEb": True, "PI_VALUEf": 0.0, "PI_VALUEb": True},
            {"INDEX": 2, "TAG": "HMI_TramStopTime", "HMI_VALUEi": i + 1, "HMI_VALUEb": True, "PI_VALUEf": 0.0, "PI_VALUEb": True},
            {"INDEX": 3, "TAG": "HMI_AllQuietb", "HMI_VALUEi": i + 2, "HMI_VALUEb": False, "PI_VALUEf": 0.0, "PI_VALUEb": True},
            {"INDEX": 4, "TAG": "HMI_LIGHTONOFFb", "HMI_VALUEi": i + 3, "HMI_VALUEb": True, "PI_VALUEf": 0.0, "PI_VALUEb": True},
            {"INDEX": 5, "TAG": "HMI_RR2_RR3Pwrb", "HMI_VALUEi": i + 4, "HMI_VALUEb": False, "PI_VALUEf": 0.0, "PI_VALUEb": True},
        ]
        response = client.post('/api/hmi/send-updates',
                              data=json.dumps(update_data),
                              content_type='application/json')
        assert response.status_code == 200, f"Iteration {i}: Batch POST failed"
        data = json.loads(response.data)
        assert data['updated_count'] == 5, f"Iteration {i}: Expected 5 updates, got {data['updated_count']}"

        # Verify all updates
        with db_lock:
            for j in range(1, 6):
                record = db.search(query.INDEX == j)
                expected_value = i + (j - 1)
                assert record[0]['HMI_VALUEi'] == expected_value, f"Iteration {i}: INDEX {j} value mismatch"

    print("Successfully completed 100 iterations of batch updates")

