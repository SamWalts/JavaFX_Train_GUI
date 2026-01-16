"""
REST Client Module - Provides REST API communication with the train control server.
This module contains the REST client class that can be used by any GUI (Tkinter, JavaFX, etc.)
or by automated scripts.
"""
import json
import logging
import requests
from tinydb import TinyDB, Query
from tinydb.storages import MemoryStorage

# Configure logging
logger = logging.getLogger("rest_client_module")

# Default server configuration
DEFAULT_REST_SERVER_URL = "http://127.0.0.1:5000"


class RESTClient:
    """REST API client for communicating with the train control server.
    
    This client provides methods to interact with the REST server's endpoints:
    - Health check
    - Get all data
    - Check for HMI updates
    - Get HMI updates  
    - Send HMI updates
    - Debug print database
    """
    
    def __init__(self, base_url=DEFAULT_REST_SERVER_URL):
        """Initialize the REST client.
        
        Args:
            base_url: Base URL of the REST server (default: http://127.0.0.1:5000)
        """
        self.base_url = base_url
        self.session = requests.Session()
        self.connected = False
        
    def check_health(self):
        """Check if the server is healthy.
        
        Returns:
            dict: Health status with 'status' and 'db_count' keys, or None if failed.
        """
        try:
            response = self.session.get(f"{self.base_url}/health", timeout=5)
            if response.status_code == 200:
                self.connected = True
                return response.json()
            self.connected = False
            return None
        except requests.exceptions.RequestException as e:
            logger.error(f"Health check failed: {e}")
            self.connected = False
            return None
    
    def get_all_data(self):
        """Get all database records from server.
        
        Returns:
            list: List of all database records, or None if failed.
        """
        try:
            response = self.session.get(f"{self.base_url}/api/hmi/get-all", timeout=10)
            if response.status_code == 200:
                return response.json()
            logger.error(f"Failed to get all data: {response.status_code}")
            return None
        except (requests.exceptions.RequestException, json.JSONDecodeError) as e:
            logger.error(f"Failed to get all data: {e}")
            return None
    
    def check_hmi_updates(self):
        """Check if there are updates for HMI (HMI_READi == 1).
        
        Returns:
            dict: Result with 'has_updates' (bool) and 'count' (int) keys.
        """
        try:
            response = self.session.get(f"{self.base_url}/api/hmi/check-updates", timeout=5)
            if response.status_code == 200:
                return response.json()
            return {"has_updates": False, "count": 0}
        except requests.exceptions.RequestException as e:
            logger.debug(f"Failed to check HMI updates: {e}")
            return {"has_updates": False, "count": 0}
    
    def get_hmi_updates(self):
        """Get updates for HMI from server.
        
        Returns:
            list: List of updated records, or empty list if failed.
        """
        try:
            response = self.session.get(f"{self.base_url}/api/hmi/get-updates", timeout=10)
            if response.status_code == 200:
                return response.json()
            return []
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to get HMI updates: {e}")
            return []
    
    def send_hmi_updates(self, data):
        """Send HMI updates to server.
        
        Args:
            data: List of records to send to server.
            
        Returns:
            dict: Response with 'success', 'updated_count', 'updated_indexes', or None if failed.
        """
        try:
            response = self.session.post(
                f"{self.base_url}/api/hmi/send-updates",
                json=data,
                timeout=10
            )
            if response.status_code == 200:
                return response.json()
            logger.error(f"Failed to send HMI updates: {response.status_code}")
            return None
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to send HMI updates: {e}")
            return None
    
    def print_server_db(self):
        """Request server to print database (debug endpoint).
        
        Returns:
            list: All database records, or None if failed.
        """
        try:
            response = self.session.get(f"{self.base_url}/api/debug/print-db", timeout=10)
            if response.status_code == 200:
                return response.json()
            return None
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to print server DB: {e}")
            return None
    
    def close(self):
        """Close the session."""
        self.session.close()
        self.connected = False


def LoadGUIDB(GUIdb):
    """Initialize the local GUI database with default values.
    
    Args:
        GUIdb: TinyDB instance to populate with default records.
        
    This creates 80 records matching the server's database structure:
    - Records 1-21: HMI control values
    - Records 22-49: Future HMI slots
    - Records 50-52: Speed values
    - Records 53-64: Switch feedback entries
    - Records 65-70: Tram station entries
    - Records 71-80: Future PI slots
    """
    # HMI control records (1-21)
    GUIdb.insert({"INDEX": 1, "TAG": "HMI_RHT", "HMI_VALUEi": 25, "HMI_VALUEb": False, "PI_VALUEf": 0.0, "PI_VALUEb": True, "HMI_READi": 0})
    GUIdb.insert({"INDEX": 2, "TAG": "HMI_TramStopTime", "HMI_VALUEi": 10, "HMI_VALUEb": True, "PI_VALUEf": 0.0, "PI_VALUEb": True, "HMI_READi": 0})
    GUIdb.insert({"INDEX": 3, "TAG": "HMI_AllQuietb", "HMI_VALUEi": 0, "HMI_VALUEb": False, "PI_VALUEf": 0.0, "PI_VALUEb": True, "HMI_READi": 0})
    GUIdb.insert({"INDEX": 4, "TAG": "HMI_LIGHTONOFFb", "HMI_VALUEi": 0, "HMI_VALUEb": True, "PI_VALUEf": 0.0, "PI_VALUEb": True, "HMI_READi": 0})
    GUIdb.insert({"INDEX": 5, "TAG": "HMI_RR2_RR3Pwrb", "HMI_VALUEi": 0, "HMI_VALUEb": False, "PI_VALUEf": 0.0, "PI_VALUEb": True, "HMI_READi": 0})
    GUIdb.insert({"INDEX": 6, "TAG": "HMI_RRBellb", "HMI_VALUEi": 0, "HMI_VALUEb": True, "PI_VALUEf": 0.0, "PI_VALUEb": True, "HMI_READi": 0})
    GUIdb.insert({"INDEX": 7, "TAG": "HMI_RRDieselSteamb", "HMI_VALUEi": 0, "HMI_VALUEb": False, "PI_VALUEf": 0.0, "PI_VALUEb": True, "HMI_READi": 0})
    GUIdb.insert({"INDEX": 8, "TAG": "HMI_RRHornb", "HMI_VALUEi": 0, "HMI_VALUEb": True, "PI_VALUEf": 0.0, "PI_VALUEb": True, "HMI_READi": 0})
    GUIdb.insert({"INDEX": 9, "TAG": "HMI_RRQuietb", "HMI_VALUEi": 0, "HMI_VALUEb": False, "PI_VALUEf": 0.0, "PI_VALUEb": True, "HMI_READi": 0})
    GUIdb.insert({"INDEX": 10, "TAG": "HMI_RRWhistleb", "HMI_VALUEi": 0, "HMI_VALUEb": True, "PI_VALUEf": 0.0, "PI_VALUEb": True, "HMI_READi": 0})
    GUIdb.insert({"INDEX": 11, "TAG": "HMI_Switch1ABb", "HMI_VALUEi": 0, "HMI_VALUEb": True, "PI_VALUEf": 0.0, "PI_VALUEb": True, "HMI_READi": 0})
    GUIdb.insert({"INDEX": 12, "TAG": "HMI_Switch2RR3b", "HMI_VALUEi": 0, "HMI_VALUEb": True, "PI_VALUEf": 0.0, "PI_VALUEb": True, "HMI_READi": 0})
    GUIdb.insert({"INDEX": 13, "TAG": "HMI_Switch3RR4b", "HMI_VALUEi": 0, "HMI_VALUEb": True, "PI_VALUEf": 0.0, "PI_VALUEb": True, "HMI_READi": 0})
    GUIdb.insert({"INDEX": 14, "TAG": "HMI_Switch4RR3b", "HMI_VALUEi": 0, "HMI_VALUEb": True, "PI_VALUEf": 0.0, "PI_VALUEb": True, "HMI_READi": 0})
    GUIdb.insert({"INDEX": 15, "TAG": "HMI_Switch5ABb", "HMI_VALUEi": 0, "HMI_VALUEb": True, "PI_VALUEf": 0.0, "PI_VALUEb": True, "HMI_READi": 0})
    GUIdb.insert({"INDEX": 16, "TAG": "HMI_Switch6ABb", "HMI_VALUEi": 0, "HMI_VALUEb": True, "PI_VALUEf": 0.0, "PI_VALUEb": True, "HMI_READi": 0})
    GUIdb.insert({"INDEX": 17, "TAG": "HMI_TramQuietb", "HMI_VALUEi": 0, "HMI_VALUEb": True, "PI_VALUEf": 0.0, "PI_VALUEb": True, "HMI_READi": 0})
    GUIdb.insert({"INDEX": 18, "TAG": "HMI_TramStpStn_2b", "HMI_VALUEi": 0, "HMI_VALUEb": True, "PI_VALUEf": 0.0, "PI_VALUEb": True, "HMI_READi": 0})
    GUIdb.insert({"INDEX": 19, "TAG": "HMI_TramStpStn_3b", "HMI_VALUEi": 0, "HMI_VALUEb": False, "PI_VALUEf": 0.0, "PI_VALUEb": True, "HMI_READi": 0})
    GUIdb.insert({"INDEX": 20, "TAG": "HMI_TramStpStn_5b", "HMI_VALUEi": 0, "HMI_VALUEb": True, "PI_VALUEf": 0.0, "PI_VALUEb": True, "HMI_READi": 0})
    GUIdb.insert({"INDEX": 21, "TAG": "HMI_TramStpStn_6b", "HMI_VALUEi": 0, "HMI_VALUEb": False, "PI_VALUEf": 0.0, "PI_VALUEb": True, "HMI_READi": 0})
    
    # Future HMI slots (22-49)
    for i in range(22, 50):
        GUIdb.insert({"INDEX": i, "TAG": f"HMI_Future_{i-21}", "HMI_VALUEi": 0, "HMI_VALUEb": True, "PI_VALUEf": 0.0, "PI_VALUEb": True, "HMI_READi": 0})
    
    # PI/Speed entries (50-52)
    GUIdb.insert({"INDEX": 50, "TAG": "RR1ABspeed_HMI", "HMI_VALUEi": 0, "HMI_VALUEb": True, "PI_VALUEf": 9.12, "PI_VALUEb": True, "HMI_READi": 0})
    GUIdb.insert({"INDEX": 51, "TAG": "RR1CDspeed_HMI", "HMI_VALUEi": 0, "HMI_VALUEb": True, "PI_VALUEf": 0.12, "PI_VALUEb": True, "HMI_READi": 0})
    GUIdb.insert({"INDEX": 52, "TAG": "RR2ABspeed_HMI", "HMI_VALUEi": 0, "HMI_VALUEb": True, "PI_VALUEf": 0.12, "PI_VALUEb": True, "HMI_READi": 0})
    
    # Switch main feedback entries (53-64)
    GUIdb.insert({"INDEX": 53, "TAG": "Switch1Main_HMIb", "HMI_VALUEi": 0, "HMI_VALUEb": True, "PI_VALUEf": 0.12, "PI_VALUEb": True, "HMI_READi": 0})
    GUIdb.insert({"INDEX": 54, "TAG": "open", "HMI_VALUEi": 0, "HMI_VALUEb": True, "PI_VALUEf": 0.12, "PI_VALUEb": False, "HMI_READi": 0})
    GUIdb.insert({"INDEX": 55, "TAG": "Switch2RR3Main_HMIb", "HMI_VALUEi": 0, "HMI_VALUEb": True, "PI_VALUEf": 0.12, "PI_VALUEb": True, "HMI_READi": 0})
    GUIdb.insert({"INDEX": 56, "TAG": "open", "HMI_VALUEi": 0, "HMI_VALUEb": True, "PI_VALUEf": 0.12, "PI_VALUEb": False, "HMI_READi": 0})
    GUIdb.insert({"INDEX": 57, "TAG": "Switch3RR4Main_HMIb", "HMI_VALUEi": 0, "HMI_VALUEb": True, "PI_VALUEf": 0.12, "PI_VALUEb": True, "HMI_READi": 0})
    GUIdb.insert({"INDEX": 58, "TAG": "open", "HMI_VALUEi": 0, "HMI_VALUEb": True, "PI_VALUEf": 0.12, "PI_VALUEb": False, "HMI_READi": 0})
    GUIdb.insert({"INDEX": 59, "TAG": "Switch4RR3Main_HMIb", "HMI_VALUEi": 0, "HMI_VALUEb": True, "PI_VALUEf": 0.12, "PI_VALUEb": True, "HMI_READi": 0})
    GUIdb.insert({"INDEX": 60, "TAG": "open", "HMI_VALUEi": 0, "HMI_VALUEb": True, "PI_VALUEf": 0.12, "PI_VALUEb": False, "HMI_READi": 0})
    GUIdb.insert({"INDEX": 61, "TAG": "Switch5Main_HMIb", "HMI_VALUEi": 0, "HMI_VALUEb": True, "PI_VALUEf": 0.12, "PI_VALUEb": True, "HMI_READi": 0})
    GUIdb.insert({"INDEX": 62, "TAG": "open", "HMI_VALUEi": 0, "HMI_VALUEb": True, "PI_VALUEf": 0.12, "PI_VALUEb": True, "HMI_READi": 0})
    GUIdb.insert({"INDEX": 63, "TAG": "Switch6Main_HMIb", "HMI_VALUEi": 0, "HMI_VALUEb": True, "PI_VALUEf": 0.12, "PI_VALUEb": True, "HMI_READi": 0})
    GUIdb.insert({"INDEX": 64, "TAG": "RR2orRR3Pwr_HMIb", "HMI_VALUEi": 0, "HMI_VALUEb": True, "PI_VALUEf": 0.12, "PI_VALUEb": True, "HMI_READi": 0})
    
    # Tram station entries (65-70)
    GUIdb.insert({"INDEX": 65, "TAG": "TramStn1_HMIb", "HMI_VALUEi": 0, "HMI_VALUEb": True, "PI_VALUEf": 0.12, "PI_VALUEb": False, "HMI_READi": 0})
    GUIdb.insert({"INDEX": 66, "TAG": "TramStn2_HMIb", "HMI_VALUEi": 0, "HMI_VALUEb": True, "PI_VALUEf": 0.12, "PI_VALUEb": False, "HMI_READi": 0})
    GUIdb.insert({"INDEX": 67, "TAG": "TramStn3_HMIb", "HMI_VALUEi": 0, "HMI_VALUEb": True, "PI_VALUEf": 0.12, "PI_VALUEb": False, "HMI_READi": 0})
    GUIdb.insert({"INDEX": 68, "TAG": "TramStn4_HMIb", "HMI_VALUEi": 0, "HMI_VALUEb": True, "PI_VALUEf": 0.12, "PI_VALUEb": True, "HMI_READi": 0})
    GUIdb.insert({"INDEX": 69, "TAG": "TramStn5_HMIb", "HMI_VALUEi": 0, "HMI_VALUEb": True, "PI_VALUEf": 0.12, "PI_VALUEb": False, "HMI_READi": 0})
    GUIdb.insert({"INDEX": 70, "TAG": "TramStn6_HMIb", "HMI_VALUEi": 0, "HMI_VALUEb": True, "PI_VALUEf": 0.12, "PI_VALUEb": False, "HMI_READi": 0})
    
    # Future PI slots (71-80)
    for i in range(71, 81):
        GUIdb.insert({"INDEX": i, "TAG": f"PI_Future_{i-70}", "HMI_VALUEi": 0, "HMI_VALUEb": True, "PI_VALUEf": 0.12, "PI_VALUEb": False, "HMI_READi": 0})
    
    logger.info(f"Local GUI database initialized with {len(GUIdb)} records")


def connect_to_server(rest_client, GUIdb, query, max_retries=20):
    """Attempt to connect to the REST server and fetch initial data.
    
    Args:
        rest_client: RESTClient instance
        GUIdb: TinyDB instance for local data
        query: TinyDB Query instance
        max_retries: Maximum connection attempts (default: 20)
        
    Returns:
        tuple: (success: bool, message: str)
    """
    import time
    
    for i in range(max_retries):
        health = rest_client.check_health()
        if health:
            logger.info(f"Connected to server: {health}")
            
            # Fetch initial data from server
            all_data = rest_client.get_all_data()
            if all_data:
                # Update local database with server data
                for record in all_data:
                    index = record.get("INDEX")
                    if index:
                        GUIdb.update({
                            "HMI_VALUEi": record.get("HMI_VALUEi", 0),
                            "HMI_VALUEb": record.get("HMI_VALUEb", False),
                            "PI_VALUEf": record.get("PI_VALUEf", 0.0),
                            "PI_VALUEb": record.get("PI_VALUEb", True),
                            "HMI_READi": record.get("HMI_READi", 0)
                        }, query.INDEX == index)
                logger.info(f"Loaded {len(all_data)} records from server")
            
            return True, f"Connected! DB has {health.get('db_count', 0)} records"
        else:
            logger.info(f"Connection attempt {i+1}/{max_retries} failed, retrying...")
            time.sleep(1.0)
    
    logger.error("Failed to connect to REST server after max retries")
    return False, "Failed to connect to server!"


def poll_server(rest_client, GUIdb, query):
    """Poll the server for updates via REST API.
    
    This function checks for updates from the server and sends any pending
    local updates to the server.
    
    Args:
        rest_client: RESTClient instance
        GUIdb: TinyDB instance for local data
        query: TinyDB Query instance
        
    Returns:
        tuple: (received_count: int, sent_count: int)
    """
    received_count = 0
    sent_count = 0
    
    try:
        # Check for updates from server (HMI_READi == 1)
        check_result = rest_client.check_hmi_updates()
        if check_result.get("has_updates", False):
            # Fetch the updates
            updates = rest_client.get_hmi_updates()
            if updates:
                logger.info(f"Received {len(updates)} updates from server")
                for record in updates:
                    index = record.get("INDEX")
                    if index:
                        GUIdb.update({
                            "HMI_VALUEi": record.get("HMI_VALUEi", 0),
                            "HMI_VALUEb": record.get("HMI_VALUEb", False),
                            "PI_VALUEf": record.get("PI_VALUEf", 0.0),
                            "PI_VALUEb": record.get("PI_VALUEb", True),
                            "HMI_READi": 0  # Mark as processed
                        }, query.INDEX == index)
                received_count = len(updates)
        
        # Send local updates to server (HMI_READi > 0)
        pending_updates = GUIdb.search(query.HMI_READi > 0)
        if pending_updates:
            result = rest_client.send_hmi_updates(pending_updates)
            if result and result.get("success"):
                # Clear the flags after successful send
                for record in pending_updates:
                    GUIdb.update({"HMI_READi": 0}, query.INDEX == record.get("INDEX"))
                logger.info(f"Sent {len(pending_updates)} updates to server")
                sent_count = len(pending_updates)
                
    except Exception as e:
        logger.error(f"Poll error: {e}")
    
    return received_count, sent_count
