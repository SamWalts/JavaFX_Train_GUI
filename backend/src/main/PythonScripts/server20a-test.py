''' ******************SERVER**************
Starts 2 threads and monitors and controls from within thread
****************************************'''
'''**************************************************************************************************************
 Setup flags for HMI and PI
 'PINew'              PI requests new HMI data? 'PINewb', When True has data to send
            Server responds with "PIYes" for new data, "PINo" for no change
 'HMINew'             HMI requests new PI data? 'HMINewb', When True has data to send
             Server responds with "HMIYes" for new data, "HMINo" for no change
 'ServerSendUpdatestoPI'      PI requests only update (Based on 'PIYes'). 
            Server waits until 'PIReadytoRecv', then sends 
 'ServerSendUpdatestoHMI'     PI requests only update (Based on 'PIYes').
            Server waits until 'HMIReadytoRecv', then sends 
 'PIReadytoRecv'      PI ready to receive data, following 'PIYes'
            Server sends data, either Entire DB or just Updates
 'HMIReadytoRecv'     HMI ready to receive data, following 'HMIYes'
            Server sends data, either Entire DB or just Update
 'ServerSendEntiretoPI'  PI request entire DB be sent, waits on 'HMIReadytoRecv'
            Server sends DB as list(list(dictionary)). Waits on 'HMIReadytoRecv'
 'ServerSendEntiretoHMI'  HMI request entire DB be sent, waits on 'HMIReadytoRecv'
            Server sends DB in JSON format?? Waits on 'HMIReadytoRecv'
'ServerReadytoRecv'      Server ready to receive from either PI or HMIS
'PISendingUpdate'       PI to send updates to Server. Waits on 'ServerReadytoRecv'
'HMISendingUpdate'       HMI to send updates to Server. Waits on 'ServerReadytoRecv'
'''
import json
import socket
from socket import error as SocketError
import errno
import threading
import time
# from json import loads as json_loads
from json import dumps as json_dumps, loads as json_loads
# from threading import Event
from tinydb import TinyDB, Query
from tinydb.storages import MemoryStorage
import logging
from logging.handlers import RotatingFileHandler

# ---------- Logging setup ----------
logger = logging.getLogger("server20a-test")
logger.setLevel(logging.INFO)
_formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s')
# File handler (rotating)
_file_handler = RotatingFileHandler('server20a-test.log', maxBytes=1_000_000, backupCount=3)
_file_handler.setFormatter(_formatter)
# Console handler
_console_handler = logging.StreamHandler()
_console_handler.setFormatter(_formatter)
if not logger.handlers:
    logger.addHandler(_file_handler)
    logger.addHandler(_console_handler)

# Connection Data
HOST = '127.0.0.1'
PORT = 55556
FORMAT = "utf-8"
RECV_BUFFER_SIZE = 12244  # Buffer size for socket recv
SLEEP_SHORT = 0.050  # Short sleep interval (50ms)
SLEEP_MEDIUM = 0.100  # Medium sleep interval (100ms)
SLEEP_LONG = 0.400  # Long sleep interval (400ms)
cltmsg="pass"
global PIstatus, HMIstatus, SeverRdyb, db, SaveDBb
PIstatus = "PINo"  # other is "PIYes"
HMIstatus = "HMINo"
paulstatus = "paulNo"
ServerRdyb = False

db = TinyDB(storage=MemoryStorage)
#CachingMiddleware.WRITE_CACHE_SIZE = 1000 writes

# Thread lock for database operations to ensure thread safety
db_lock = threading.Lock()

# Starting Server
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#allow reuse of address
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind((HOST, PORT))
server.listen(4)  # 4 cients max
Xstatus = 2
# Lists For Clients and Their Nicknames

query = Query()  # query object

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
    db.insert({"INDEX": 57, "TAG": "Switch3RR4Main_HMIb", "HMI_VALUEi": 0, "HMI_VALUEb": True, "PI_VALUEf": 0.12,"PI_VALUEb": True, "HMI_READi": 0})
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
    db.insert({"INDEX": 77, "TAG": "PI_Future_7", "HMI_VALUEi": 0, "HMI_VALUEb": True, "PI_VALUEf": 0.12, "PI_VALUEb": False,"HMI_READi": 0})
    db.insert({"INDEX": 78, "TAG": "PI_Future_8", "HMI_VALUEi": 0, "HMI_VALUEb": True, "PI_VALUEf": 0.12, "PI_VALUEb": False,"HMI_READi": 0})
    db.insert({"INDEX": 79, "TAG": "PI_Future_9", "HMI_VALUEi": 0, "HMI_VALUEb": True, "PI_VALUEf": 0.12, "PI_VALUEb": False,"HMI_READi": 0})
    db.insert({"INDEX": 80, "TAG": "PI_Future_10", "HMI_VALUEi": 0, "HMI_VALUEb": True, "PI_VALUEf": 0.12, "PI_VALUEb": False,"HMI_READi": 0})

# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# Handling Messages From Clients
def handlePI(clientPI):
    """
    Handle messages from the PI client.  The client will send a message of either "PINew", "ReadytoRecv",
    "SendingUpdates", or json data.  If the message is "PINew", the server checks the database for any
    records where HMI_READi is 2 (i.e. a record which has been updated by the HMI), and sends a message back
    to the client of either "PIYes" or "PINo" depending on whether there are any such records.  If the message is
    "ReadytoRecv", the server sends a message to the client with the data from the database records where
    HMI_READi is 2.  The client should then update the PI system with this data.  If the message is
    "SendingUpdates", the client is ready to send data to the server, so the server sends a message back to
    the client saying "ServerReady".  The client should then send the data to the server, which will be in
    json format.  The server will then update the database with this data.  If the message is json data, the
    server should update the database with this data.  The client should then send a message to the server
    saying "ClientSENDDone", and the server should respond with "pass".

    Parameters:
    clientPI (socket): The socket for the PI client.

    Global variables used:
    PIstatus (bool): Whether the PI client is connected or not.
    ToUpdate (bool): Whether the server should update the database from the PI client or not.
    """
    global PIstatus, ToUpdate
    logger.info("PI handle started")
    """ *** UPDATE BELOW FOR EACH CLIENT ***"""
    ClientHMI_ReadiNum = 2 # this is for PI ** UPDATE FOR EACH **
    PseudoClient = clientPI
    #Pseudoclientmsg is set by program
    """ should work with no change below"""
    while True:
        time.sleep(SLEEP_SHORT)
        PIclientmsg = PseudoClient.recv(RECV_BUFFER_SIZE).decode(FORMAT)
        #print("PI msg at top: ", PIclientmsg)
        if PIclientmsg == "PINew":
            logger.info("PINew received from PI")
            #print(db.count(query.HMI_READi == 2))      #check db & answer
            with db_lock:
                if db.count(query.HMI_READi == 2) > 0: clientPI.sendall("PIYes".encode(FORMAT))
                else: clientPI.send("PINo".encode(FORMAT)) # no updates
            #time.sleep(0.100)
        elif PIclientmsg == "ReadytoRecv": # waiting
            logger.info("ReadytoRecv received from PI")
            with db_lock:
                Clientdata = db.search(query.HMI_READi == 2) # get server updates for PI
                logger.info("PI data: %s", Clientdata)
                json_data = json.dumps(Clientdata)
                clientPI.sendall(json_data.encode(FORMAT))  # Send updates to PI
                db.update({"HMI_READi": 0}, query.HMI_READi == ClientHMI_ReadiNum) # set where HMI_READi=2 to 0
            time.sleep(SLEEP_LONG)
            clientPI.send("ServerSENDDone".encode(FORMAT))
            time.sleep(SLEEP_LONG)
            clientPI.send("pass".encode(FORMAT))
        # sent data, now wait for PI to send data or flag none
        elif PIclientmsg == "SendingUpdates":
            logger.info("SendingUpdates received from PI")
            clientPI.send("ServerReady".encode(FORMAT))
        elif PIclientmsg.find('[') >= 0 or PIclientmsg.find('{') >= 0: # waiting on data
            # Support possible coalesced 'ClientSENDDone' in same buffer
            payload = PIclientmsg
            if "ClientSENDDone" in payload:
                payload, _, _ = payload.partition("ClientSENDDone")
                Updatetinydb(payload)
                clientPI.send("pass".encode(FORMAT))
            else:
                Updatetinydb(payload) # json loads in Updatetinydb, sent in bytes
        elif PIclientmsg == "ClientSENDDone":
            logger.info("got ClientSENDDone from PI")
            clientPI.send("pass".encode(FORMAT))
            time.sleep(SLEEP_SHORT)
# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# Handling Messages From Clients
def handleHMI(clientHMI):
    """
    Handle messages from the HMI client following the same pattern as handlePI.
    All messages sent to HMI include newline character as required by the protocol for the java side.

    Parameters:
    clientHMI (socket): The socket for the HMI client.

    Global variables used:
    HMIstatus (bool): Whether the HMI client is connected or not.
    ToUpdate (bool): Whether the server should update the database from the HMI client or not.
    """
    global HMIstatus, ToUpdate
    logger.info("HMI handle started")
    clientHMI.sendall(("pass\n").encode(FORMAT))

    # Send initial full database to HMI on connection
    with db_lock:
        HMIClientData = db.all()
        HMIJsonData = json.dumps(HMIClientData)
    clientHMI.sendall((HMIJsonData + "\n").encode(FORMAT))

    # Wrap socket for line-based reading to avoid partial/multiple message issues
    f = clientHMI.makefile('r', encoding=FORMAT, newline='\n')

    while True:
        time.sleep(SLEEP_SHORT)
        try:
            line = f.readline()
        except (ConnectionResetError, OSError) as e:
            logger.info("HMI connection error: %s", e)
            break
        if not line:
            logger.info("HMI connection closed by peer")
            break
        clientHMImsg = line.rstrip("\r\n")
        if not clientHMImsg:
            continue
        # Only log non-poll messages to avoid noisy logs
        if clientHMImsg != "HMINew":
            logger.info("[HMI<-] %s", clientHMImsg)

        if clientHMImsg == "HMINew":
            # Check db for records where HMI_READi == 1 (PI updates destined for HMI)
            with db_lock:
                if db.count(query.HMI_READi > 0) > 0:
                    clientHMI.sendall("HMIYes\n".encode(FORMAT))
                else:
                    clientHMI.sendall("HMINo\n".encode(FORMAT))

        elif clientHMImsg == "ReadytoRecv":
            logger.info("ReadytoRecv received from HMI")
            # Get updates where HMI_READi == 1 (PI updates only)
            with db_lock:
                HMIdata = db.search(query.HMI_READi > 0)
                json_data = json.dumps(HMIdata)
            clientHMI.sendall((json_data + "\n").encode(FORMAT))

            # Clear the read flags for those items now delivered to HMI
            # db.update({"HMI_READi": 1}, query.HMI_READi == 1)

            time.sleep(SLEEP_LONG)
            clientHMI.send("ServerSENDDone\n".encode(FORMAT))
            time.sleep(SLEEP_LONG)
            clientHMI.send("pass\n".encode(FORMAT))

        elif clientHMImsg == "SendingUpdates":
            logger.info("SendingUpdates received from HMI")
            clientHMI.send("ServerReady\n".encode(FORMAT))

        elif clientHMImsg.find('[{"INDEX"') >= 0:
            logger.info("got data from HMI: %s", clientHMImsg)
            Updatetinydb(clientHMImsg)
            # Acknowledge to HMI that updates were applied
            clientHMI.send("ServerSENDDone\n".encode(FORMAT))
            clientHMI.send("pass\n".encode(FORMAT))

        elif clientHMImsg == "ClientSENDDone":
            logger.info("got ClientSENDDone from HMI")
            clientHMI.send("pass\n".encode(FORMAT))

        elif clientHMImsg == "Print Server":
            logger.info("Print Server command received from HMI")
            for row in db:
                logger.info(str(row))
            clientHMI.send("pass\n".encode(FORMAT))


# Handling Messages to/from GUI   Sends HMI(GUI) receives PI
# TODO: Investigate why this client is not getting data to be recognized in the java program.

# Handling Messages to/from GUI   Sends HMI(GUI) receives PI
def handlepaul(clientpaul):
    """
    Handle messages from the paul client.  The client will send a message of either "paulNew",
    "ReadytoRecv", "SendingUpdates", or json data.  If the message is "paulNew", the server checks
    the database for any records where HMI_READi is 2 (i.e. a record which has been updated by the
    HMI), and sends a message back to the client of either "paulYes" or "paulNo" depending on whether
    there are any such records.  If the message is "ReadytoRecv", the server sends a message to the
    client with the data from the database records where HMI_READi is 2.  The client should then
    update the PI system with this data.  If the message is "SendingUpdates", the client is ready to
    send data to the server, so the server sends a message back to the client saying "ServerReady".
    The client should then send the data to the server, which will be in json format.  The server will
    then update the database with this data.  If the message is json data, the server should update
    the database with this data.  The client should then send a message to the server saying
    "ClientSENDDone", and the server should respond with "pass".

    Parameters:
    clientpaul (socket): The socket for the paul client.

    Global variables used:
    PIstatus (bool): Whether the PI client is connected or not.
    ToUpdate (bool): Whether the server should update the database from the PI client or not.
    """
    global PIstatus, ToUpdate
    logger.info("paul handle started")
    """ *** UPDATE BELOW FOR EACH CLIENT ***"""
    PseudoClient = clientpaul # ** UPDATE FOR EACH **
    #Pseudoclientmsg is set by program
    #PseudoClientdata = "paulClientdata" # used in prints  ** UPDATE FOR EACH **
    #PseudoClient.send("paulYes".encode(FORMAT))

    while True:
        Pseudoclientmsg = PseudoClient.recv(RECV_BUFFER_SIZE).decode(FORMAT)
        #print("PAUL msg at top: ", Pseudoclientmsg)
        time.sleep(SLEEP_SHORT)
        if Pseudoclientmsg == "paulNew":
            #check db & answer (only items flagged for paul consumption of HMI-origin updates, i.e., HMI_READi == 2)
            with db_lock:
                if db.count(query.HMI_READi > 0) > 0:
                    message = "paulYes"
                    PseudoClient.send(message.encode(FORMAT))
                else:
                    PseudoClient.send("paulNo".encode(FORMAT))  # no updates
            time.sleep(0.075)  # Slightly longer than SLEEP_SHORT for paul response
            #PseudoClient.send("pass".encode(FORMAT))
        elif Pseudoclientmsg == "ReadytoRecv":
            # Send only HMI-origin updates to paul
            with db_lock:
                Clientdata = db.search(query.HMI_READi >= 0)  # get server updates for paul
                logger.info("Paul data & length: %s : %s", Clientdata, len(Clientdata))
                json_data = json.dumps(Clientdata)
                PseudoClient.sendall(json_data.encode(FORMAT))  # Send updates to paul
            time.sleep(SLEEP_LONG)
            # TODO: fix logic to wait until PI confirms receipt before clearing flags
            # For now, just clear all HMI_READi flags since paul is assumed to have consumed them
            # db.update({"HMI_READi": 0}, query.HMI_READi >= 1)  # set where HMI_READi>=1 to 0
            # Better: Clear only PI-origin notifications (1) now that paul consumed them
            with db_lock:
                db.update({"HMI_READi": 0}, query.HMI_READi == 1)
            time.sleep(SLEEP_MEDIUM)
            # Clear only HMI-origin notifications (2) now that paul consumed them
            with db_lock:
                db.update({"HMI_READi": 0}, query.HMI_READi == 2)
            time.sleep(SLEEP_MEDIUM)
            PseudoClient.send("ServerSENDDone".encode(FORMAT))
            time.sleep(SLEEP_MEDIUM)
            PseudoClient.send("pass".encode(FORMAT))

        # sent data, now wait for PI to send data or flag none
        elif Pseudoclientmsg == "SendingUpdates":
            logger.info("SendingUpdates received from paul")
            PseudoClient.send("ServerReady".encode(FORMAT))
        elif Pseudoclientmsg.find("INDEX") >= 0: # waiting on data
            logger.info("got data from paul: ")
            # Handle case where JSON and ClientSENDDone or poll tokens coalesce
            msg = Pseudoclientmsg
            # Strip any leading probe tokens like 'paulNew' that can prefix JSON
            if msg.startswith("paulNew"):
                msg = msg[len("paulNew"):]
            # Extract first JSON object/array from the buffer
            start_brace = msg.find('{')
            start_bracket = msg.find('[')
            starts = [i for i in [start_brace, start_bracket] if i != -1]
            if starts:
                start = min(starts)
                # find matching ending; try last '}' or ']' in buffer
                end_brace = msg.rfind('}')
                end_bracket = msg.rfind(']')
                ends = [i for i in [end_brace, end_bracket] if i != -1]
                if ends:
                    end = max(ends)
                    json_part = msg[start:end+1]
                else:
                    json_part = msg[start:]
            else:
                json_part = msg
            if "ClientSENDDone" in json_part:
                json_part, _, _ = json_part.partition("ClientSENDDone")
            logger.info("clientpaulmsg b4 send to updatetinydb: %s", json_part)
            Updatetinydb(json_part)
        elif Pseudoclientmsg == "ClientSENDDone":
            logger.info("got ClientSENDDone from paul")
            PseudoClient.send("pass".encode(FORMAT))
        elif Pseudoclientmsg == "Print Server":
            for row in db:
                logger.info(str(row))
            PseudoClient.send("pass".encode(FORMAT))

# ^^^^ Receiving for initial run with client ^^^^^^^^^
def receive():
    """
    Handles incoming connections and starts threads for the PI, HMI, paul, and sam clients.

    The server will only accept one connection from each of these clients.  If a client with the same
    nickname is already connected, the server will not accept the new connection.  The server will
    send a message to the client saying "Connected to server!" after accepting the connection.  The
    server will then start a thread for the client, and send a message to the client saying "pass".
    """
    logger.info("Receive in loop")
    PIRunningb, HMIRunningb, paulRunningb = False, False, False # start threads once
    while True:
        # Accept Connection
        time.sleep(SLEEP_SHORT)

        client, address = server.accept()
        logger.info("Connected with %s", str(address))

        # Request And Store Nickname
        client.send('NICK'.encode(FORMAT))
        logger.info("I just sent: NICK")
        try:
            nickname = client.recv(1024).decode(FORMAT).strip()  # Add strip() to remove whitespace
        except SocketError as err:
            if err.errno != errno.ECONNRESET: raise
            client.close()
            break
        # Print And Broadcast Nickname
        logger.info("Nickname is %s", str(nickname))
        if nickname == "pass": pass
        #broadcast("{} joined!".format(nickname).encode('FORMAT'))
        # Start Handling Threads For Clients, only handle these 4 clients
        if nickname == "PI": # nickname and prevent multi instances
            if not PIRunningb:
                clientPI = client
                try:
                    clientPI.send('Connected to server!'.encode(FORMAT))
                    handlePI_thread = threading.Thread(target=handlePI, args=(clientPI,), daemon=True)
                    time.sleep(SLEEP_MEDIUM)
                    clientPI.send('pass'.encode(FORMAT))
                    handlePI_thread.start()
                except OSError as e:
                    logger.info("PI send failed during handshake: %s", e)
            PIRunningb = True # flag to prevent multi instances
        elif nickname == "HMI": # nickname and prevent multi instances
            clientHMI = client
            if not HMIRunningb:
                try:
                    clientHMI.send('Connected to server!\n'.encode(FORMAT))
                    handleHMI_thread = threading.Thread(target=handleHMI, args=(clientHMI,),daemon=True)
                    time.sleep(SLEEP_MEDIUM)
                    # Removed extra 'pass' here; handleHMI will send initial pass and DB JSON
                    handleHMI_thread.start()
                except OSError as e:
                    logger.info("HMI send failed during handshake: %s", e)
            HMIRunningb = True
        elif nickname == "paul": # nickname and prevent multi instances
            clientpaul = client
            if not paulRunningb:
                try:
                    clientpaul.send('Connected to server!'.encode(FORMAT))
                    time.sleep(SLEEP_MEDIUM)
                    clientpaul.send('pass'.encode(FORMAT))
                    handlepaul_thread = threading.Thread(target=handlepaul, args=(clientpaul,),daemon=True)
                    handlepaul_thread.start()
                except OSError as e:
                    logger.info("paul send failed during handshake: %s", e)
            paulRunningb = True
        elif nickname == "sam":
            pass
        else:
            logger.info("Client not found!")
            logger.info(str(nickname))

#   ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
# SERVER PROVIDES UPDATES TO CLIENTS
def ClientgetDBUpdate(Xstatus):
    """
    ClientgetDBUpdate searches the database for records where HMI_READi is equal to Xstatus.
    It returns a json string of the results, or an empty list if none are found.

    Parameters:
    Xstatus (int): The value of HMI_READi to search for.

    Returns:
    str: A json string of the results, or an empty list if none are found.
    """
    temp1 = []
    logger.info("In ClientgetDBUpdate")
    try:
        #for i in range(81):
        #temp1=db.search(query["HMI_READi"] == Xstatus)
        with db_lock:
            if db.search(query["HMI_READi"] == Xstatus):
                temp1.append(db.search(query["HMI_READi"] == Xstatus))
                ToUpdate = json.dumps(temp1)
    except IndexError:
        logger.exception("ClientGetDBUpdate Exception! line 534")
        pass
    try:
        if temp1 == []: pass  # if =none then set to blank
    except:
        ToUpdate = []
    return ToUpdate

#   ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
# UPDATE THE TINY DB from either
#^^^^^^^^^ UPDATE TINY DB ^^^^^^^^^^^
def Updatetinydb(ToUpdateDB: str):  #ToUpdateDB is a nested list
    """
    Updatetinydb updates the tinydb database with the given nested list of json data.

    Parameters:
    ToUpdateDB (list): A nested list of json data to be written to the database.

    Returns:
    None
    """
    logger.info("ToUpdateDB for json_loads: %s", ToUpdateDB)
    json_data = [] # clear register
    if not ToUpdateDB or not ToUpdateDB.strip():
        return
    s = ToUpdateDB.lstrip()
    if not (s.startswith("{") or s.startswith("[")):
        logger.warning("[WARN] Skipping non-JSON payload: %s", ToUpdateDB[:200])
        return

    # Parse and update DB; preserve incoming HMI_READi if provided; default to 2 for HMI-origin updates
    try:
        json_data = json_loads(ToUpdateDB)
        # Ensure we handle a single object or a list
        if isinstance(json_data, dict):
            json_data = [json_data]
        
        with db_lock:
            for item in json_data:
                Index = item.get("INDEX")
                if Index is None:
                    logger.warning("[WARN] Skipping item with missing INDEX: %s", item)
                    continue
                # Validate INDEX is an integer
                if not isinstance(Index, int):
                    logger.warning("[WARN] Skipping item with non-integer INDEX: %s", Index)
                    continue
                tag = item.get("TAG")
                HMI_Valuei = item.get("HMI_VALUEi")
                HMI_Valueb = item.get("HMI_VALUEb")
                PI_Valuef = item.get("PI_VALUEf")
                PI_Valueb = item.get("PI_VALUEb")
                incoming_readi = item.get("HMI_READi")
                # If incoming value missing, assume HMI-origin update
                new_hmi_readi = incoming_readi if incoming_readi is not None else 2
                db.update({
                    "HMI_VALUEi": HMI_Valuei,
                    "HMI_VALUEb": HMI_Valueb,
                    "PI_VALUEf": PI_Valuef,
                    "PI_VALUEb": PI_Valueb,
                    "HMI_READi": new_hmi_readi
                }, query.INDEX == Index)
                logger.info("update done for INDEX %s TAG=%s HMI_READi=%s", Index, tag, new_hmi_readi)

                # Mirror switch command to its backend main feedback tag so frontend receives a MAIN update post-ACK
                if tag in SWITCH_MAIN_MAP:
                    main_tag = SWITCH_MAIN_MAP[tag]
                    # Determine new state preference: use HMI_VALUEb if provided, else PI_VALUEb
                    new_state = HMI_Valueb if HMI_Valueb is not None else PI_Valueb
                    if new_state is not None:
                        updated = db.update({
                            "PI_VALUEb": new_state,
                            # Mark as a PI/server-origin change so HMI poll (HMI_READi==1) will pick it up
                            "HMI_READi": 1
                        }, query.TAG == main_tag)
                        if updated:
                            logger.info("[Mirror] Updated main tag %s PI_VALUEb=%s (from %s)", main_tag, new_state, tag)
                    else:
                        logger.info("[Mirror] Main tag %s not found to mirror from %s", main_tag, tag)
    except Exception as e:
        logger.exception("[ERROR] Failed to parse/apply JSON from HMI: %s", e)
        return

#   ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
# CLEAR SEND FLAGS IN TINY DB from either
#^^^^^^^^^ CLEAR FLAGS TINY DB ^^^^^^^^^^^
def ClearFlagsUpdatedb(dbRows, Xstatus):
    """
    ClearFlagsUpdatedb clears the send flags in the tinydb database from either PI or HMI.

    Parameters:
    dbRows (list): A nested list of json data to be updated in the database.
    Xstatus (int): A flag indicating where the update request came from. 1 is HMI, 2 is PI.

    Returns:
    None
    """
    global HMIstatus, PIstatus
    dbRows1 = json_loads(dbRows)
    with db_lock:
        for j in range(1,3):
            for i in range(len(dbRows1)):
                Index = dbRows1[i].get("INDEX", "Not Found")
                logger.info(Index)
                #??????????WAS Xstatus?????????
                db.update({"HMI_READi": 0}, query.INDEX == Index and query.HMI_READi == j)
    #db.storage.flush()  # save
    # Set Flags for client notification
    if Xstatus == 1:
        HMIstatus = "HMINo"
    elif Xstatus == 2:
        PIstatus = "PINo"

# *************************************************************
#****************************MAIN FUNCTION*********************
#db.truncate()
logger.info("db count: %s", db.count(query.HMI_READi == 0))
if db.count(all) < 1: # is disk db empty?
    LoadDB()
    logger.info("Server Started & created DB")
elif db.count(all)>80:
    logger.info("Server Started & DB corrupted resetting")
    db.truncate()
    LoadDB()
    logger.info("DB now at: %s", db.count(all))

receive_thread = threading.Thread(target=receive,)
receive_thread.start()
