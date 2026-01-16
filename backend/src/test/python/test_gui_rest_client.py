"""
Unit tests for REST Client Module.
Tests the REST client class and its methods.
"""
import sys
import os
import pytest
import json
from unittest.mock import Mock, patch, MagicMock

# Add the PythonScripts directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../main/PythonScripts'))

from rest_client_module import RESTClient, LoadGUIDB, connect_to_server, poll_server
from tinydb import TinyDB, Query
from tinydb.storages import MemoryStorage


class TestRESTClient:
    """Test cases for the RESTClient class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.client = RESTClient("http://127.0.0.1:5000")
    
    def test_init(self):
        """Test RESTClient initialization."""
        assert self.client.base_url == "http://127.0.0.1:5000"
        assert self.client.connected == False
        assert self.client.session is not None
    
    @patch('requests.Session.get')
    def test_check_health_success(self, mock_get):
        """Test successful health check."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "healthy", "db_count": 80}
        mock_get.return_value = mock_response
        
        result = self.client.check_health()
        
        assert result == {"status": "healthy", "db_count": 80}
        assert self.client.connected == True
        mock_get.assert_called_once_with("http://127.0.0.1:5000/health", timeout=5)
    
    @patch('requests.Session.get')
    def test_check_health_failure(self, mock_get):
        """Test failed health check."""
        mock_response = Mock()
        mock_response.status_code = 500
        mock_get.return_value = mock_response
        
        result = self.client.check_health()
        
        assert result is None
        assert self.client.connected == False
    
    @patch('requests.Session.get')
    def test_check_health_connection_error(self, mock_get):
        """Test health check with connection error."""
        import requests
        mock_get.side_effect = requests.exceptions.ConnectionError("Connection refused")
        
        result = self.client.check_health()
        
        assert result is None
        assert self.client.connected == False
    
    @patch('requests.Session.get')
    def test_get_all_data_success(self, mock_get):
        """Test getting all data from server."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = [{"INDEX": 1, "TAG": "HMI_RHT"}]
        mock_get.return_value = mock_response
        
        result = self.client.get_all_data()
        
        assert result == [{"INDEX": 1, "TAG": "HMI_RHT"}]
        mock_get.assert_called_once_with("http://127.0.0.1:5000/api/hmi/get-all", timeout=10)
    
    @patch('requests.Session.get')
    def test_get_all_data_failure(self, mock_get):
        """Test failed get all data request."""
        mock_response = Mock()
        mock_response.status_code = 500
        mock_get.return_value = mock_response
        
        result = self.client.get_all_data()
        
        assert result is None
    
    @patch('requests.Session.get')
    def test_check_hmi_updates_with_updates(self, mock_get):
        """Test checking HMI updates when updates exist."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"has_updates": True, "count": 2}
        mock_get.return_value = mock_response
        
        result = self.client.check_hmi_updates()
        
        assert result == {"has_updates": True, "count": 2}
        mock_get.assert_called_once_with("http://127.0.0.1:5000/api/hmi/check-updates", timeout=5)
    
    @patch('requests.Session.get')
    def test_check_hmi_updates_without_updates(self, mock_get):
        """Test checking HMI updates when no updates exist."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"has_updates": False, "count": 0}
        mock_get.return_value = mock_response
        
        result = self.client.check_hmi_updates()
        
        assert result == {"has_updates": False, "count": 0}
    
    @patch('requests.Session.get')
    def test_get_hmi_updates_success(self, mock_get):
        """Test getting HMI updates from server."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = [{"INDEX": 1, "TAG": "HMI_RHT", "HMI_VALUEi": 30}]
        mock_get.return_value = mock_response
        
        result = self.client.get_hmi_updates()
        
        assert len(result) == 1
        assert result[0]["INDEX"] == 1
        mock_get.assert_called_once_with("http://127.0.0.1:5000/api/hmi/get-updates", timeout=10)
    
    @patch('requests.Session.get')
    def test_get_hmi_updates_empty(self, mock_get):
        """Test getting HMI updates when no updates exist."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = []
        mock_get.return_value = mock_response
        
        result = self.client.get_hmi_updates()
        
        assert result == []
    
    @patch('requests.Session.post')
    def test_send_hmi_updates_success(self, mock_post):
        """Test sending HMI updates to server."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"success": True, "updated_count": 1, "updated_indexes": [1]}
        mock_post.return_value = mock_response
        
        update_data = [{"INDEX": 1, "TAG": "HMI_RHT", "HMI_VALUEi": 30}]
        result = self.client.send_hmi_updates(update_data)
        
        assert result["success"] == True
        assert result["updated_count"] == 1
        mock_post.assert_called_once()
    
    @patch('requests.Session.post')
    def test_send_hmi_updates_failure(self, mock_post):
        """Test failed send HMI updates request."""
        mock_response = Mock()
        mock_response.status_code = 500
        mock_post.return_value = mock_response
        
        result = self.client.send_hmi_updates([{"INDEX": 1}])
        
        assert result is None
    
    @patch('requests.Session.get')
    def test_print_server_db_success(self, mock_get):
        """Test debug print server database."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = [{"INDEX": 1}]
        mock_get.return_value = mock_response
        
        result = self.client.print_server_db()
        
        assert result == [{"INDEX": 1}]
        mock_get.assert_called_once_with("http://127.0.0.1:5000/api/debug/print-db", timeout=10)


class TestLoadGUIDB:
    """Test cases for the LoadGUIDB function."""
    
    def test_load_gui_db_creates_80_records(self):
        """Test that LoadGUIDB creates 80 records."""
        GUIdb = TinyDB(storage=MemoryStorage)
        LoadGUIDB(GUIdb)
        
        assert len(GUIdb) == 80
    
    def test_load_gui_db_creates_correct_first_record(self):
        """Test that LoadGUIDB creates correct first record."""
        GUIdb = TinyDB(storage=MemoryStorage)
        query = Query()
        LoadGUIDB(GUIdb)
        
        record = GUIdb.search(query.INDEX == 1)
        assert len(record) == 1
        assert record[0]['TAG'] == 'HMI_RHT'
        assert record[0]['HMI_VALUEi'] == 25
        assert record[0]['HMI_READi'] == 0
    
    def test_load_gui_db_creates_speed_records(self):
        """Test that LoadGUIDB creates speed records."""
        GUIdb = TinyDB(storage=MemoryStorage)
        query = Query()
        LoadGUIDB(GUIdb)
        
        record = GUIdb.search(query.INDEX == 50)
        assert len(record) == 1
        assert record[0]['TAG'] == 'RR1ABspeed_HMI'
        assert record[0]['PI_VALUEf'] == 9.12
    
    def test_load_gui_db_creates_switch_records(self):
        """Test that LoadGUIDB creates switch feedback records."""
        GUIdb = TinyDB(storage=MemoryStorage)
        query = Query()
        LoadGUIDB(GUIdb)
        
        record = GUIdb.search(query.INDEX == 53)
        assert len(record) == 1
        assert record[0]['TAG'] == 'Switch1Main_HMIb'
    
    def test_load_gui_db_creates_tram_station_records(self):
        """Test that LoadGUIDB creates tram station records."""
        GUIdb = TinyDB(storage=MemoryStorage)
        query = Query()
        LoadGUIDB(GUIdb)
        
        for i in range(65, 71):
            record = GUIdb.search(query.INDEX == i)
            assert len(record) == 1
            assert 'TramStn' in record[0]['TAG']


class TestRESTClientEdgeCases:
    """Test edge cases and error handling for RESTClient."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.client = RESTClient("http://127.0.0.1:5000")
    
    @patch('requests.Session.get')
    def test_timeout_handling(self, mock_get):
        """Test timeout error handling."""
        import requests
        mock_get.side_effect = requests.exceptions.Timeout("Request timed out")
        
        result = self.client.check_health()
        
        assert result is None
        assert self.client.connected == False
    
    @patch('requests.Session.post')
    def test_send_empty_list(self, mock_post):
        """Test sending empty update list."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"success": True, "updated_count": 0, "updated_indexes": []}
        mock_post.return_value = mock_response
        
        result = self.client.send_hmi_updates([])
        
        assert result["success"] == True
        assert result["updated_count"] == 0
    
    @patch('requests.Session.get')
    def test_invalid_json_response(self, mock_get):
        """Test handling of invalid JSON response."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.side_effect = json.JSONDecodeError("Invalid JSON", "", 0)
        mock_get.return_value = mock_response
        
        # The client should handle this gracefully by returning None
        result = self.client.get_all_data()
        
        assert result is None
