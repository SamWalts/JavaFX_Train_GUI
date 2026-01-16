"""
REST Server - Replacement for server20a.py
Provides REST API endpoints for HMI and PI clients to interact with TinyDB.
"""
import json
import logging
from logging.handlers import RotatingFileHandler
from flask import Flask, request, jsonify
from tinydb import TinyDB, Query
from tinydb.storages import MemoryStorage
import threading

# ---------- Logging setup ----------
logger = logging.getLogger("rest_server")
logger.setLevel(logging.INFO)
_formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s')

# File handler (rotating)
_file_handler = RotatingFileHandler('rest_server.log', maxBytes=1_000_000, backupCount=3)
_file_handler.setFormatter(_formatter)

# Console handler
_console_handler = logging.StreamHandler()
_console_handler.setFormatter(_formatter)

if not logger.handlers:
    logger.addHandler(_file_handler)
    logger.addHandler(_console_handler)

# Initialize Flask app
app = Flask(__name__)

# Initialize TinyDB with in-memory storage
db = TinyDB(storage=MemoryStorage)
query = Query()

# Lock for thread-safe database operations
db_lock = threading.Lock()

# Mapping from HMI command switch tags to backend main feedback tags
SWITCH_MAIN_MAP = {
    "HMI_Switch1ABb": "Switch1Main_HMIb",
    "HMI_Switch2RR3b": "Switch2RR3Main_HMIb",
    "HMI_Switch3RR4b": "Switch3RR4Main_HMIb",
    "HMI_Switch4RR3b": "Switch4RR3Main_HMIb",
    "HMI_Switch5ABb": "Switch5Main_HMIb",
    "HMI_Switch6ABb": "Switch6Main_HMIb",
}

def LoadDB():
    """Initialize the database with default values."""
    with db_lock:
        db.insert({"INDEX": 1, "TAG": "HMI_RHT", "HMI_VALUEi": 25, "HMI_VALUEb": False, "PI_VALUEf": 0.0, "PI_VALUEb": True,"HMI_READi": 0})
        db.insert({"INDEX": 2, "TAG": "HMI_TramStopTime", "HMI_VALUEi": 10, "HMI_VALUEb": True, "PI_VALUEf": 0.0,"PI_VALUEb": True, "HMI_READi": 0})
        db.insert({"INDEX": 3, "TAG": "HMI_AllQuietb", "HMI_VALUEi": 0, "HMI_VALUEb": False, "PI_VALUEf": 0.0, "PI_VALUEb": True,"HMI_READi": 0})
        db.insert({"INDEX": 4, "TAG": "HMI_LIGHTONOFFb", "HMI_VALUEi": 0, "HMI_VALUEb": True, "PI_VALUEf": 0.0, "PI_VALUEb": True,"HMI_READi": 0})
        db.insert({"INDEX": 5, "TAG": "HMI_RR2_RR3Pwrb", "HMI_VALUEi": 0, "HMI_VALUEb": False, "PI_VALUEf": 0.0,"PI_VALUEb": True, "HMI_READi": 0})
        db.insert({"INDEX": 6, "TAG": "HMI_RRBellb", "HMI_VALUEi": 0, "HMI_VALUEb": True, "PI_VALUEf": 0.0, "PI_VALUEb":True,"HMI_READi": 0})
        db.insert({"INDEX": 7, "TAG": "HMI_RRDieselSteamb", "HMI_VALUEi": 0, "HMI_VALUEb": False, "PI_VALUEf": 0.0,"PI_VALUEb": True, "HMI_READi": 0})
        db.insert({"INDEX": 8, "TAG": "HMI_RRHornb", "HMI_VALUEi": 0, "HMI_VALUEb": True, "PI_VALUEf": 0.0, "PI_VALUEb": True,"HMI_READi": 0})
        db.insert({"INDEX": 9, "TAG": "HMI_RRQuietb", "HMI_VALUEi": 0, "HMI_VALUEb": False, "PI_VALUEf": 0.0, "PI_VALUEb": True,"HMI_READi": 0})
        db.insert({"INDEX": 10, "TAG": "HMI_RRWhistleb", "HMI_VALUEi": 0, "HMI_VALUEb": True, "PI_VALUEf": 0.0, "PI_VALUEb": True,"HMI_READi": 0})
        db.insert({"INDEX": 11, "TAG": "HMI_Switch1ABb", "HMI_VALUEi": 0, "HMI_VALUEb": True, "PI_VALUEf": 0.0, "PI_VALUEb": True,"HMI_READi": 0})
        db.insert({"INDEX": 12, "TAG": "HMI_Switch2RR3b", "HMI_VALUEi": 0, "HMI_VALUEb": True, "PI_VALUEf": 0.0,"PI_VALUEb": True, "HMI_READi": 0})
        db.insert({"INDEX": 13, "TAG": "HMI_Switch3RR4b", "HMI_VALUEi": 0, "HMI_VALUEb": True, "PI_VALUEf": 0.0,"PI_VALUEb": True, "HMI_READi": 0})
        db.insert({"INDEX": 14, "TAG": "HMI_Switch4RR3b", "HMI_VALUEi": 0, "HMI_VALUEb": True, "PI_VALUEf": 0.0,"PI_VALUEb": True, "HMI_READi": 0})
        db.insert({"INDEX": 15, "TAG": "HMI_Switch5ABb", "HMI_VALUEi": 0, "HMI_VALUEb": True, "PI_VALUEf": 0.0,"PI_VALUEb": True, "HMI_READi": 0})
        db.insert({"INDEX": 16, "TAG": "HMI_Switch6ABb", "HMI_VALUEi": 0, "HMI_VALUEb": True, "PI_VALUEf": 0.0, "PI_VALUEb": True,"HMI_READi": 0})
        db.insert({"INDEX": 17, "TAG": "HMI_TramQuietb", "HMI_VALUEi": 0, "HMI_VALUEb": True, "PI_VALUEf": 0.0, "PI_VALUEb": True,"HMI_READi": 0})
        db.insert({"INDEX": 18, "TAG": "HMI_TramStpStn_2b", "HMI_VALUEi": 0, "HMI_VALUEb": True, "PI_VALUEf": 0.0,"PI_VALUEb": True, "HMI_READi": 0})
        db.insert({"INDEX": 19, "TAG": "HMI_TramStpStn_3b", "HMI_VALUEi": 0, "HMI_VALUEb": False, "PI_VALUEf": 0.0,"PI_VALUEb": True, "HMI_READi": 0})
        db.insert({"INDEX": 20, "TAG": "HMI_TramStpStn_5b", "HMI_VALUEi": 0, "HMI_VALUEb": True, "PI_VALUEf": 0.0,"PI_VALUEb": True, "HMI_READi": 0})
        db.insert({"INDEX": 21, "TAG": "HMI_TramStpStn_6b", "HMI_VALUEi": 0, "HMI_VALUEb": False, "PI_VALUEf": 0.0,"PI_VALUEb": True, "HMI_READi": 0})
        db.insert({"INDEX": 22, "TAG": "HMI_Future_1", "HMI_VALUEi": 0, "HMI_VALUEb": True, "PI_VALUEf": 0.0, "PI_VALUEb": True,"HMI_READi": 0})
        db.insert({"INDEX": 23, "TAG": "HMI_Future_2", "HMI_VALUEi": 0, "HMI_VALUEb": True, "PI_VALUEf": 0.0, "PI_VALUEb": True,"HMI_READi": 0})
        db.insert({"INDEX": 24, "TAG": "HMI_Future_3", "HMI_VALUEi": 0, "HMI_VALUEb": True, "PI_VALUEf": 0.0, "PI_VALUEb": True,"HMI_READi": 0})
        db.insert({"INDEX": 25, "TAG": "HMI_Future_4", "HMI_VALUEi": 0, "HMI_VALUEb": True, "PI_VALUEf": 0.0, "PI_VALUEb": True,"HMI_READi": 0})
        db.insert({"INDEX": 26, "TAG": "HMI_Future_5", "HMI_VALUEi": 0, "HMI_VALUEb": True, "PI_VALUEf": 0.0, "PI_VALUEb": True,"HMI_READi": 0})
        db.insert({"INDEX": 27, "TAG": "HMI_Future_6", "HMI_VALUEi": 0, "HMI_VALUEb": True, "PI_VALUEf": 0.0, "PI_VALUEb": True,"HMI_READi": 0})
        db.insert({"INDEX": 28, "TAG": "HMI_Future_7", "HMI_VALUEi": 0, "HMI_VALUEb": True, "PI_VALUEf": 0.0, "PI_VALUEb": True,"HMI_READi": 0})
        db.insert({"INDEX": 29, "TAG": "HMI_Future_8", "HMI_VALUEi": 0, "HMI_VALUEb": True, "PI_VALUEf": 0.0, "PI_VALUEb": True,"HMI_READi": 0})
        db.insert({"INDEX": 30, "TAG": "HMI_Future_9", "HMI_VALUEi": 0, "HMI_VALUEb": True, "PI_VALUEf": 0.0, "PI_VALUEb": True,"HMI_READi": 0})
        db.insert({"INDEX": 31, "TAG": "HMI_Future_10", "HMI_VALUEi": 0, "HMI_VALUEb": True, "PI_VALUEf": 0.0, "PI_VALUEb": True,"HMI_READi": 0})
        db.insert({"INDEX": 32, "TAG": "HMI_Future_11", "HMI_VALUEi": 0, "HMI_VALUEb": True, "PI_VALUEf": 0.0, "PI_VALUEb": True,"HMI_READi": 0})
        db.insert({"INDEX": 33, "TAG": "HMI_Future_12", "HMI_VALUEi": 0, "HMI_VALUEb": True, "PI_VALUEf": 0.0, "PI_VALUEb": True,"HMI_READi": 0})
        db.insert({"INDEX": 34, "TAG": "HMI_Future_13", "HMI_VALUEi": 0, "HMI_VALUEb": True, "PI_VALUEf": 0.0, "PI_VALUEb": True,"HMI_READi": 0})
        db.insert({"INDEX": 35, "TAG": "HMI_Future_14", "HMI_VALUEi": 0, "HMI_VALUEb": True, "PI_VALUEf": 0.0, "PI_VALUEb": True,"HMI_READi": 0})
        db.insert({"INDEX": 36, "TAG": "HMI_Future_15", "HMI_VALUEi": 0, "HMI_VALUEb": True, "PI_VALUEf": 0.0, "PI_VALUEb": True,"HMI_READi": 0})
        db.insert({"INDEX": 37, "TAG": "HMI_Future_16", "HMI_VALUEi": 0, "HMI_VALUEb": True, "PI_VALUEf": 0.0, "PI_VALUEb": True,"HMI_READi": 0})
        db.insert({"INDEX": 38, "TAG": "HMI_Future_17", "HMI_VALUEi": 0, "HMI_VALUEb": True, "PI_VALUEf": 0.0, "PI_VALUEb": True,"HMI_READi": 0})
        db.insert({"INDEX": 39, "TAG": "HMI_Future_18", "HMI_VALUEi": 0, "HMI_VALUEb": True, "PI_VALUEf": 0.0, "PI_VALUEb": True,"HMI_READi": 0})
        db.insert({"INDEX": 40, "TAG": "HMI_Future_19", "HMI_VALUEi": 0, "HMI_VALUEb": True, "PI_VALUEf": 0.0, "PI_VALUEb": True,"HMI_READi": 0})
        db.insert({"INDEX": 41, "TAG": "HMI_Future_20", "HMI_VALUEi": 0, "HMI_VALUEb": True, "PI_VALUEf": 0.0, "PI_VALUEb": True,"HMI_READi": 0})
        db.insert({"INDEX": 42, "TAG": "HMI_Future_21", "HMI_VALUEi": 0, "HMI_VALUEb": True, "PI_VALUEf": 0.0, "PI_VALUEb": True,"HMI_READi": 0})
        db.insert({"INDEX": 43, "TAG": "HMI_Future_22", "HMI_VALUEi": 0, "HMI_VALUEb": True, "PI_VALUEf": 0.0, "PI_VALUEb": True,"HMI_READi": 0})
        db.insert({"INDEX": 44, "TAG": "HMI_Future_23", "HMI_VALUEi": 0, "HMI_VALUEb": True, "PI_VALUEf": 0.0, "PI_VALUEb": True,"HMI_READi": 0})
        db.insert({"INDEX": 45, "TAG": "HMI_Future_24", "HMI_VALUEi": 0, "HMI_VALUEb": True, "PI_VALUEf": 0.0, "PI_VALUEb": True,"HMI_READi": 0})
        db.insert({"INDEX": 46, "TAG": "HMI_Future_25", "HMI_VALUEi": 0, "HMI_VALUEb": True, "PI_VALUEf": 0.0, "PI_VALUEb": True,"HMI_READi": 0})
        db.insert({"INDEX": 47, "TAG": "HMI_Future_26", "HMI_VALUEi": 0, "HMI_VALUEb": True, "PI_VALUEf": 0.0, "PI_VALUEb": True,"HMI_READi": 0})
        db.insert({"INDEX": 48, "TAG": "HMI_Future_27", "HMI_VALUEi": 0, "HMI_VALUEb": True, "PI_VALUEf": 0.0, "PI_VALUEb": True,"HMI_READi": 0})
        db.insert({"INDEX": 49, "TAG": "HMI_Future_28", "HMI_VALUEi": 0, "HMI_VALUEb": True, "PI_VALUEf": 0.0, "PI_VALUEb": True,"HMI_READi": 0})
        db.insert({"INDEX": 50, "TAG": "RR1ABspeed_HMI", "HMI_VALUEi": 0, "HMI_VALUEb": True, "PI_VALUEf": 0.12,"PI_VALUEb": True, "HMI_READi": 0})
        db.insert({"INDEX": 51, "TAG": "RR1CDspeed_HMI", "HMI_VALUEi": 0, "HMI_VALUEb": True, "PI_VALUEf": 0.12,"PI_VALUEb": True, "HMI_READi": 0})
        db.insert({"INDEX": 52, "TAG": "RR2ABspeed_HMI", "HMI_VALUEi": 0, "HMI_VALUEb": True, "PI_VALUEf": 0.12,"PI_VALUEb": True, "HMI_READi": 0})
        db.insert({"INDEX": 53, "TAG": "Switch1Main_HMIb", "HMI_VALUEi": 0, "HMI_VALUEb": True, "PI_VALUEf": 0.12,"PI_VALUEb": False, "HMI_READi": 0})
        db.insert({"INDEX": 54, "TAG": "open", "HMI_VALUEi": 0, "HMI_VALUEb": True, "PI_VALUEf": 0.12, "PI_VALUEb": False,"HMI_READi": 0})
        db.insert({"INDEX": 55, "TAG": "Switch2RR3Main_HMIb", "HMI_VALUEi": 0, "HMI_VALUEb": True, "PI_VALUEf": 0.12,"PI_VALUEb": False, "HMI_READi": 0})
        db.insert({"INDEX": 56, "TAG": "open", "HMI_VALUEi": 0, "HMI_VALUEb": True, "PI_VALUEf": 0.12, "PI_VALUEb": False,"HMI_READi": 0})
        db.insert({"INDEX": 57, "TAG": "Switch3RR4Main_HMIb", "HMI_VALUEiy": 0, "HMI_VALUEb": True, "PI_VALUEf": 0.12,"PI_VALUEb": True, "HMI_READi": 0})
        db.insert({"INDEX": 58, "TAG": "open", "HMI_VALUEi": 0, "HMI_VALUEb": True, "PI_VALUEf": 0.12, "PI_VALUEb": False,"HMI_READi": 0})
        db.insert({"INDEX": 59, "TAG": "Switch4RR3Main_HMIb", "HMI_VALUEi": 0, "HMI_VALUEb": True, "PI_VALUEf": 0.12,"PI_VALUEb": False, "HMI_READi": 0})
        db.insert({"INDEX": 60, "TAG": "open", "HMI_VALUEi": 0, "HMI_VALUEb": True, "PI_VALUEf": 0.12, "PI_VALUEb": False,"HMI_READi": 0})
        db.insert({"INDEX": 61, "TAG": "Switch5Main_HMIb", "HMI_VALUEi": 0, "HMI_VALUEb": True, "PI_VALUEf": 0.12,"PI_VALUEb": False, "HMI_READi": 0})
        db.insert({"INDEX": 62, "TAG": "open", "HMI_VALUEi": 0, "HMI_VALUEb": True, "PI_VALUEf": 0.12, "PI_VALUEb": True,"HMI_READi": 0})
        db.insert({"INDEX": 63, "TAG": "Switch6Main_HMIb", "HMI_VALUEi": 0, "HMI_VALUEb": True, "PI_VALUEf": 0.12,"PI_VALUEb": False, "HMI_READi": 0})
        db.insert({"INDEX": 64, "TAG": "RR2orRR3Pwr_HMIb", "HMI_VALUEi": 0, "HMI_VALUEb": True, "PI_VALUEf": 0.12,"PI_VALUEb": False, "HMI_READi": 0})
        db.insert({"INDEX": 65, "TAG": "TramStn1_HMIb", "HMI_VALUEi": 0, "HMI_VALUEb": True, "PI_VALUEf": 0.12,"PI_VALUEb": False, "HMI_READi": 0})
        db.insert({"INDEX": 66, "TAG": "TramStn2_HMIb", "HMI_VALUEi": 0, "HMI_VALUEb": True, "PI_VALUEf": 0.12,"PI_VALUEb": False, "HMI_READi": 0})
        db.insert({"INDEX": 67, "TAG": "TramStn3_HMIb", "HMI_VALUEi": 0, "HMI_VALUEb": True, "PI_VALUEf": 0.12,"PI_VALUEb": False, "HMI_READi": 0})
        db.insert({"INDEX": 68, "TAG": "TramStn4_HMIb", "HMI_VALUEi": 0, "HMI_VALUEb": True, "PI_VALUEf": 0.12, "PI_VALUEb": True,"HMI_READi": 0})
        db.insert({"INDEX": 69, "TAG": "TramStn5_HMIb", "HMI_VALUEi": 0, "HMI_VALUEb": True, "PI_VALUEf": 0.12,"PI_VALUEb": False, "HMI_READi": 0})
        db.insert({"INDEX": 70, "TAG": "TramStn6_HMIb", "HMI_VALUEi": 0, "HMI_VALUEb": True, "PI_VALUEf": 0.12,"PI_VALUEb": False, "HMI_READi": 0})
        db.insert({"INDEX": 71, "TAG": "PI_Future_1", "HMI_VALUEi": 0, "HMI_VALUEb": True, "PI_VALUEf": 0.12, "PI_VALUEb": False,"HMI_READi": 0})
        db.insert({"INDEX": 72, "TAG": "PI_Future_2", "HMI_VALUEi": 0, "HMI_VALUEb": True, "PI_VALUEf": 0.12, "PI_VALUEb": False,"HMI_READi": 0})
        db.insert({"INDEX": 73, "TAG": "PI_Future_3", "HMI_VALUEi": 0, "HMI_VALUEb": True, "PI_VALUEf": 0.12, "PI_VALUEb": False,"HMI_READi": 0})
        db.insert({"INDEX": 74, "TAG": "PI_Future_4", "HMI_VALUEi": 0, "HMI_VALUEb": True, "PI_VALUEf": 0.12, "PI_VALUEb": False,"HMI_READi": 0})
        db.insert({"INDEX": 75, "TAG": "PI_Future_5", "HMI_VALUEi": 0, "HMI_VALUEb": True, "PI_VALUEf": 0.12, "PI_VALUEb": False,"HMI_READi": 0})
        db.insert({"INDEX": 76, "TAG": "PI_Future_6", "HMI_VALUEi": 0, "HMI_VALUEb": True, "PI_VALUEf": 0.12, "PI_VALUEb": False,"HMI_READi": 0})
        db.insert({"INDEX": 77, "TAG": "PI_Future_6", "HMI_VALUEi": 0, "HMI_VALUEb": True, "PI_VALUEf": 0.12, "PI_VALUEb": False,"HMI_READi": 0})
        db.insert({"INDEX": 78, "TAG": "PI_Future_8", "HMI_VALUEi": 0, "HMI_VALUEb": True, "PI_VALUEf": 0.12, "PI_VALUEb": False,"HMI_READi": 0})
        db.insert({"INDEX": 79, "TAG": "PI_Future_9", "HMI_VALUEi": 0, "HMI_VALUEb": True, "PI_VALUEf": 0.12, "PI_VALUEb": False,"HMI_READi": 0})
        db.insert({"INDEX": 80, "TAG": "PI_Future_10", "HMI_VALUEi": 0, "HMI_VALUEb": True, "PI_VALUEf": 0.12, "PI_VALUEb": False,"HMI_READi": 0})
        logger.info("Database initialized with 80 records")

def update_tinydb(data_list):
    """
    Update the TinyDB database with the given data list.
    
    Args:
        data_list: List of dictionaries containing database updates
        
    Returns:
        List of updated indexes
    """
    updated_indexes = []
    
    with db_lock:
        # Ensure we handle a single object or a list
        if isinstance(data_list, dict):
            data_list = [data_list]
            
        for item in data_list:
            index_val = item.get("INDEX")
            if index_val is None:
                continue
                
            tag = item.get("TAG")
            hmi_valuei = item.get("HMI_VALUEi")
            hmi_valueb = item.get("HMI_VALUEb")
            pi_valuef = item.get("PI_VALUEf")
            pi_valueb = item.get("PI_VALUEb")
            incoming_readi = item.get("HMI_READi")
            
            # If incoming value missing, assume HMI-origin update
            new_hmi_readi = incoming_readi if incoming_readi is not None else 2
            
            db.update({
                "HMI_VALUEi": hmi_valuei,
                "HMI_VALUEb": hmi_valueb,
                "PI_VALUEf": pi_valuef,
                "PI_VALUEb": pi_valueb,
                "HMI_READi": new_hmi_readi
            }, query.INDEX == index_val)
            
            logger.info(f"Updated INDEX {index_val} TAG={tag} HMI_READi={new_hmi_readi}")
            updated_indexes.append(index_val)
            
            # Mirror switch command to its backend main feedback tag
            if tag in SWITCH_MAIN_MAP:
                main_tag = SWITCH_MAIN_MAP[tag]
                new_state = hmi_valueb if hmi_valueb is not None else pi_valueb
                if new_state is not None:
                    updated = db.update({
                        "PI_VALUEb": new_state,
                        "HMI_READi": 1  # Mark as PI/server-origin change
                    }, query.TAG == main_tag)
                    if updated:
                        logger.info(f"[Mirror] Updated main tag {main_tag} PI_VALUEb={new_state} (from {tag})")
                    else:
                        logger.info(f"[Mirror] Main tag {main_tag} not found to mirror from {tag}")
                        
    return updated_indexes

# REST API Endpoints

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({"status": "healthy", "db_count": len(db)}), 200

@app.route('/api/hmi/check-updates', methods=['GET'])
def hmi_check_updates():
    """
    Check if there are updates for HMI (HMI_READi == 1).
    Equivalent to HMINew in socket protocol.
    """
    with db_lock:
        count = db.count(query.HMI_READi == 1)
    
    has_updates = count > 0
    logger.debug(f"HMI check updates: {has_updates} (count={count})")
    
    return jsonify({
        "has_updates": has_updates,
        "count": count
    }), 200

@app.route('/api/hmi/get-updates', methods=['GET'])
def hmi_get_updates():
    """
    Get updates for HMI (HMI_READi == 1).
    Equivalent to ReadytoRecv in socket protocol.
    """
    with db_lock:
        updates = db.search(query.HMI_READi == 1)
        # Clear the read flags after sending
        db.update({"HMI_READi": 0}, query.HMI_READi == 1)
    
    logger.info(f"Sending {len(updates)} updates to HMI")
    return jsonify(updates), 200

@app.route('/api/hmi/send-updates', methods=['POST'])
def hmi_send_updates():
    """
    Receive updates from HMI.
    Equivalent to SendingUpdates in socket protocol.
    """
    try:
        data = request.get_json()
        if data is None:
            return jsonify({"error": "No data provided"}), 400
        
        # Handle empty list/dict gracefully
        if not data:
            return jsonify({
                "success": True,
                "updated_count": 0,
                "updated_indexes": []
            }), 200
        
        logger.info(f"Received {len(data) if isinstance(data, list) else 1} updates from HMI")
        updated_indexes = update_tinydb(data)
        
        return jsonify({
            "success": True,
            "updated_count": len(updated_indexes),
            "updated_indexes": updated_indexes
        }), 200
        
    except Exception as e:
        logger.exception(f"Error processing HMI updates: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/hmi/get-all', methods=['GET'])
def hmi_get_all():
    """
    Get all database records for HMI.
    Sent initially when HMI connects.
    """
    with db_lock:
        all_data = db.all()
    
    logger.info(f"Sending all {len(all_data)} records to HMI")
    return jsonify(all_data), 200

@app.route('/api/pi/get-all', methods=['GET'])
def pi_get_all():
    """
    Get all database records for HMI.
    Sent initially when HMI connects.
    """
    with db_lock:
        all_data = db.all()

    logger.info(f"Sending all {len(all_data)} records to PI")
    return jsonify(all_data), 200

@app.route('/api/pi/check-updates', methods=['GET'])
def pi_check_updates():
    """
    Check if there are updates for PI (HMI_READi == 2).
    Equivalent to PINew in socket protocol.
    """
    with db_lock:
        count = db.count(query.HMI_READi == 2)

    has_updates = count > 0
    logger.debug(f"PI check updates: {has_updates} (count={count})")
    
    return jsonify({
        "has_updates": has_updates,
        "count": count
    }), 200

@app.route('/api/pi/get-updates', methods=['GET'])
def pi_get_updates():
    """
    Get updates for PI (HMI_READi == 2).
    Equivalent to ReadytoRecv in socket protocol for PI.
    """
    with db_lock:
        updates = db.search(query.HMI_READi == 2)
        # Clear the read flags after sending
        db.update({"HMI_READi": 0}, query.HMI_READi == 2)
    
    logger.info(f"Sending {len(updates)} updates to PI")
    return jsonify(updates), 200

@app.route('/api/pi/send-updates', methods=['POST'])
def pi_send_updates():
    """
    Receive updates from PI.
    Equivalent to SendingUpdates in socket protocol for PI.
    """
    try:
        data = request.get_json()
        if data is None:
            return jsonify({"error": "No data provided"}), 400
        
        # Handle empty list/dict gracefully
        if not data:
            return jsonify({
                "success": True,
                "updated_count": 0,
                "updated_indexes": []
            }), 200
        
        logger.info(f"Received {len(data) if isinstance(data, list) else 1} updates from PI")
        updated_indexes = update_tinydb(data)
        
        return jsonify({
            "success": True,
            "updated_count": len(updated_indexes),
            "updated_indexes": updated_indexes
        }), 200
        
    except Exception as e:
        logger.exception(f"Error processing PI updates: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/debug/print-db', methods=['GET'])
def debug_print_db():
    """Debug endpoint to print entire database."""
    with db_lock:
        all_data = db.all()
    
    logger.info("Database dump requested")
    for row in all_data:
        logger.info(str(row))
    
    return jsonify(all_data), 200

# Initialize database on startup
if db.count(query.INDEX >= 1) < 1:
    LoadDB()
    logger.info("Server started & created DB")
elif len(db) > 80:
    logger.info("Server started & DB corrupted, resetting")
    db.truncate()
    LoadDB()
    logger.info(f"DB now at: {len(db)}")
else:
    logger.info(f"Server started with existing DB ({len(db)} records)")

if __name__ == '__main__':
    # Run Flask server
    logger.info("Starting REST server on http://127.0.0.1:5000")
    app.run(host='127.0.0.1', port=5000, debug=False, threaded=True)
