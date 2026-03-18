"""
End-to-end integration tests for REST server.
Tests the full workflow of client-server communication.
"""
import sys
import os
import pytest
import json
import requests
import time
import subprocess
import signal

# Add the PythonScripts directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../main/PythonScripts'))

SERVER_URL = "http://127.0.0.1:5000"
SERVER_SCRIPT = os.path.join(os.path.dirname(__file__), '../../main/PythonScripts/rest_server.py')

@pytest.fixture(scope="module")
def rest_server():
    """Start the REST server for integration tests."""
    # Start the server in a subprocess
    server_process = subprocess.Popen(
        ['python3', SERVER_SCRIPT],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    # Wait for server to start
    max_retries = 10
    for i in range(max_retries):
        try:
            response = requests.get(f"{SERVER_URL}/health", timeout=1)
            if response.status_code == 200:
                break
        except requests.exceptions.ConnectionError:
            time.sleep(0.5)
    else:
        server_process.kill()
        pytest.fail("Server failed to start")
    
    yield server_process
    
    # Stop the server
    server_process.send_signal(signal.SIGTERM)
    server_process.wait(timeout=5)

def test_server_health(rest_server):
    """Test that server is healthy."""
    response = requests.get(f"{SERVER_URL}/health")
    assert response.status_code == 200
    data = response.json()
    assert data['status'] == 'healthy'
    assert data['db_count'] == 80

def test_hmi_full_workflow(rest_server):
    """Test the full HMI workflow: check, send, check, get."""
    # 1. Check for updates (should be none initially)
    response = requests.get(f"{SERVER_URL}/api/hmi/check-updates")
    assert response.status_code == 200
    assert response.json()['has_updates'] == False
    
    # 2. Send an update from HMI
    hmi_update = [{
        "INDEX": 1,
        "TAG": "HMI_RHT",
        "HMI_VALUEi": 30,
        "HMI_VALUEb": True,
        "PI_VALUEf": 0.0,
        "PI_VALUEb": True
    }]
    response = requests.post(f"{SERVER_URL}/api/hmi/send-updates", json=hmi_update)
    assert response.status_code == 200
    data = response.json()
    assert data['success'] == True
    assert data['updated_count'] == 1
    
    # 3. The update should now be available for PI (HMI_READi == 2)
    response = requests.get(f"{SERVER_URL}/api/pi/check-updates")
    assert response.status_code == 200
    assert response.json()['has_updates'] == True
    assert response.json()['count'] == 1
    
    # 4. PI gets the updates
    response = requests.get(f"{SERVER_URL}/api/pi/get-updates")
    assert response.status_code == 200
    updates = response.json()
    assert len(updates) == 1
    assert updates[0]['INDEX'] == 1
    assert updates[0]['HMI_VALUEi'] == 30
    
    # 5. After PI gets updates, they should be cleared
    response = requests.get(f"{SERVER_URL}/api/pi/check-updates")
    assert response.status_code == 200
    assert response.json()['has_updates'] == False

def test_pi_to_hmi_workflow(rest_server):
    """Test PI sending updates that HMI receives."""
    # 1. PI sends an update
    pi_update = [{
        "INDEX": 50,
        "TAG": "RR1ABspeed_HMI",
        "HMI_VALUEi": 0,
        "HMI_VALUEb": True,
        "PI_VALUEf": 0.35,
        "PI_VALUEb": True,
        "HMI_READi": 1  # Mark as PI-origin update
    }]
    response = requests.post(f"{SERVER_URL}/api/pi/send-updates", json=pi_update)
    assert response.status_code == 200
    data = response.json()
    assert data['success'] == True
    
    # 2. HMI checks for updates
    response = requests.get(f"{SERVER_URL}/api/hmi/check-updates")
    assert response.status_code == 200
    assert response.json()['has_updates'] == True
    
    # 3. HMI gets the updates
    response = requests.get(f"{SERVER_URL}/api/hmi/get-updates")
    assert response.status_code == 200
    updates = response.json()
    assert len(updates) == 1
    assert updates[0]['INDEX'] == 50
    assert updates[0]['PI_VALUEf'] == 0.35

def test_switch_mirroring_workflow(rest_server):
    """Test that switch commands are mirrored to main feedback tags."""
    # 1. HMI sends a switch command
    switch_update = [{
        "INDEX": 11,
        "TAG": "HMI_Switch1ABb",
        "HMI_VALUEi": 0,
        "HMI_VALUEb": False,
        "PI_VALUEf": 0.0,
        "PI_VALUEb": True
    }]
    response = requests.post(f"{SERVER_URL}/api/hmi/send-updates", json=switch_update)
    assert response.status_code == 200
    
    # 2. The mirrored update should be available for HMI (HMI_READi == 1)
    response = requests.get(f"{SERVER_URL}/api/hmi/check-updates")
    assert response.status_code == 200
    assert response.json()['has_updates'] == True
    
    # 3. HMI gets updates and verifies the mirrored tag
    response = requests.get(f"{SERVER_URL}/api/hmi/get-updates")
    assert response.status_code == 200
    updates = response.json()
    
    # Find the Switch1Main_HMIb record
    main_record = next((u for u in updates if u['TAG'] == 'Switch1Main_HMIb'), None)
    assert main_record is not None
    assert main_record['PI_VALUEb'] == False  # Should mirror the command

def test_get_all_database(rest_server):
    """Test getting all database records."""
    response = requests.get(f"{SERVER_URL}/api/hmi/get-all")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 80
    assert data[0]['INDEX'] == 1

def test_concurrent_updates(rest_server):
    """Test that multiple updates work correctly."""
    # Clear any pending updates first
    requests.get(f"{SERVER_URL}/api/pi/get-updates")
    
    # Send multiple updates at once
    updates = [
        {"INDEX": 1, "TAG": "HMI_RHT", "HMI_VALUEi": 40, "HMI_VALUEb": True, "PI_VALUEf": 0.0, "PI_VALUEb": True},
        {"INDEX": 2, "TAG": "HMI_TramStopTime", "HMI_VALUEi": 20, "HMI_VALUEb": False, "PI_VALUEf": 0.0, "PI_VALUEb": True},
        {"INDEX": 3, "TAG": "HMI_AllQuietb", "HMI_VALUEi": 1, "HMI_VALUEb": True, "PI_VALUEf": 0.0, "PI_VALUEb": True}
    ]
    response = requests.post(f"{SERVER_URL}/api/hmi/send-updates", json=updates)
    assert response.status_code == 200
    data = response.json()
    assert data['success'] == True
    assert data['updated_count'] == 3
    
    # Verify PI can get the updates
    response = requests.get(f"{SERVER_URL}/api/pi/get-updates")
    assert response.status_code == 200
    pi_updates = response.json()
    
    # Should have at least our 3 updates (may have more from other operations)
    indexes = [u['INDEX'] for u in pi_updates]
    assert 1 in indexes
    assert 2 in indexes
    assert 3 in indexes
