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

# Connection Data
HOST = '127.0.0.1'
PORT = 55556
FORMAT = "utf-8"
cltmsg="pass"
global PIstatus, HMIstatus, SeverRdyb, db, SaveDBb
PIstatus = "PINo"  # other is "PIYes"
HMIstatus = "HMINo"
paulstatus = "paulNo"
ServerRdyb = False

db = TinyDB(storage=MemoryStorage)
#CachingMiddleware.WRITE_CACHE_SIZE = 1000 writes

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

# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# Handling Messages From Clients
def handlePI(clientPI):
    """
    Handle messages from the PI client.  The client will send a message of either "PINew", "ReadytoRecv",
    "SendingUpdates", or json data.  If the message is "PINew", the server checks the database for any
    records where HMI_READi is 2 (i.e. a record which has been updated by the HMI), and sends a message back
    to the client of either "PIYes" or "PINo" depending on whether there are any such records.  If the message
    is "ReadytoRecv", the server sends a message to the client with the data from the database records where
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
    print("PI handle started")
    """ *** UPDATE BELOW FOR EACH CLIENT ***"""
    ClientHMI_ReadiNum = 2 # this is for PI ** UPDATE FOR EACH **
    PsuedoClient = clientPI
    #Psuedoclientmsg is set by program
    PsuedoClientdata = "PICliendtdata" # used in prints  ** UPDATE FOR EACH **
    """ should work with no change below"""
    while True:
        time.sleep(0.050)
        PIclientmsg = PsuedoClient.recv(12244).decode(FORMAT)
        #print("PI msg at top: ", PIclientmsg)
        if PIclientmsg == "PINew":
            print("PINew received from PI")
            #print(db.count(query.HMI_READi == 2))      #check db & answer
            if db.count(query.HMI_READi == 2) > 0: clientPI.sendall("PIYes".encode(FORMAT))
            else: clientPI.send("PINo".encode(FORMAT)) # no updates
            #time.sleep(0.100)
        elif PIclientmsg == "ReadytoRecv": # waiting
            print("ReadytoRecv received from PI")
            Clientdata = db.search(query.HMI_READi == 2) # get server updates for PI
            print("PI data: ", Clientdata)
            json_data = json.dumps(Clientdata)
            clientPI.sendall(json_data.encode(FORMAT))  # Send updates to PI
            db.update({"HMI_READi": 0}, query.HMI_READi == ClientHMI_ReadiNum) # set where HMI_READi=2 to 0
            time.sleep(0.400)
            clientPI.send("ServerSENDDone".encode(FORMAT))
            time.sleep(0.400)
            clientPI.send("pass".encode(FORMAT))
        # sent data, now wait for PI to send data or flag none
        elif PIclientmsg == "SendingUpdates":
            print("SendingUpdates received from PI")
            clientPI.send("ServerReady".encode(FORMAT))
        elif PIclientmsg.find('[{"INDEX"') >= 0: # waiting on data
            #print("got data from ",PI, " : ",  PIclientmsg)
            Updatetinydb(PIclientmsg) # json loads in Updatetinydb, sent in bytes
        elif PIclientmsg == "ClientSENDDone":
            print("got ClientSENDDone from PI")
            clientPI.send("pass".encode(FORMAT))
            time.sleep(0.050)
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
    print("HMI handle started")
    clientHMI.sendall(("pass\n").encode(FORMAT))

    # Send initial full database to HMI on connection
    HMIClientData = db.all()
    HMIJsonData = json.dumps(HMIClientData)
    clientHMI.sendall((HMIJsonData + "\n").encode(FORMAT))

    # Wrap socket for line-based reading to avoid partial/multiple message issues
    f = clientHMI.makefile('r', encoding=FORMAT, newline='\n')

    while True:
        time.sleep(0.050)
        line = f.readline()
        if not line:
            print("HMI connection closed by peer")
            break
        clientHMImsg = line.rstrip("\r\n")
        if not clientHMImsg:
            continue
        # Only log non-poll messages to avoid noisy logs
        if clientHMImsg != "HMINew":
            print(f"[HMI<-] {clientHMImsg}")

        if clientHMImsg == "HMINew":
            # Check db for records where HMI_READi == 1 (PI updates)
            # TODO: This should be changed to check for HMI_READi == 1
            if db.count((query.HMI_READi == 1) | (query.HMI_READi == 2)) > 0:
                clientHMI.sendall("HMIYes\n".encode(FORMAT))
            else:
                clientHMI.sendall("HMINo\n".encode(FORMAT))

        elif clientHMImsg == "ReadytoRecv":
            print("ReadytoRecv received from HMI")
            # Get updates where HMI_READi == 1 (PI updates)
            # TODO: This should be changed to check for HMI_READi == 1
            HMIdata = db.search((query.HMI_READi == 1) | (query.HMI_READi == 2))
            json_data = json.dumps(HMIdata)
            clientHMI.sendall((json_data + "\n").encode(FORMAT))

            # Clear the read flags
            # TODO: This should be changed to check for HMI_READi == 1
            db.update({"HMI_READi": 0}, (query.HMI_READi == 1) | (query.HMI_READi == 2))

            time.sleep(0.400)
            clientHMI.send("ServerSENDDone\n".encode(FORMAT))
            time.sleep(0.400)
            clientHMI.send("pass\n".encode(FORMAT))

        elif clientHMImsg == "SendingUpdates":
            print("SendingUpdates received from HMI")
            clientHMI.send("ServerReady\n".encode(FORMAT))

        elif clientHMImsg.find('[{"INDEX"') >= 0:
            print("got data from HMI: ", clientHMImsg)
            Updatetinydb(clientHMImsg)
            # Acknowledge to HMI that updates were applied
            clientHMI.send("ServerSENDDone\n".encode(FORMAT))
            clientHMI.send("pass\n".encode(FORMAT))

        elif clientHMImsg == "ClientSENDDone":
            print("got ClientSENDDone from HMI")
            clientHMI.send("pass\n".encode(FORMAT))

        elif clientHMImsg == "Print Server":
            print("Print Server command received from HMI")
            for row in db:
                print(row)
            clientHMI.send("pass\n".encode(FORMAT))


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
    print("paul handle started")
    """ *** UPDATE BELOW FOR EACH CLIENT ***"""
    PsuedoClient = clientpaul # ** UPDATE FOR EACH **
    #Psuedoclientmsg is set by program
    #PsuedoClientdata = "paulCliendtdata" # used in prints  ** UPDATE FOR EACH **
    #PsuedoClient.send("paulYes".encode(FORMAT))

    while True:
        Psuedoclientmsg = PsuedoClient.recv(12244).decode(FORMAT)
        #print("PAUL msg at top: ", Psuedoclientmsg)
        time.sleep(0.050)
        if Psuedoclientmsg == "paulNew":
            #check db & answer
            if db.count(query.HMI_READi > 0) > 0:
                message = "paulYes"
                PsuedoClient.send(message.encode(FORMAT))
            else: PsuedoClient.send("paulNo".encode(FORMAT)) # no updates
            time.sleep(0.075)
            #PsuedoClient.send("pass".encode(FORMAT))
        elif Psuedoclientmsg == "ReadytoRecv":
            Clientdata = db.search(query.HMI_READi > 0) # get local updates from both PI & HMI
            #print("Paul data & length: ", Clientdata, " : ", len(Clientdata))
            json_data = json.dumps(Clientdata)
            PsuedoClient.sendall(json_data.encode(FORMAT))  # Send updates to PI
            time.sleep(0.400)
            db.update({"HMI_READi": 0}, query.HMI_READi == 1) # PI & HMI should update, read only
            time.sleep(0.100)
            PsuedoClient.send("ServerSENDDone".encode(FORMAT))
            time.sleep(0.100)
            PsuedoClient.send("pass".encode(FORMAT))

        # sent data, now wait for PI to send data or flag none
        elif Psuedoclientmsg == "SendingUpdates":
            print("SendingUpdates received from paul")
            PsuedoClient.send("ServerReady".encode(FORMAT))
        elif Psuedoclientmsg.find("INDEX") >= 0: # waiting on data
            print("got data from paul: ")
            print("clientpaulmsg b4 send to updatetinydb: ", Psuedoclientmsg)
            Updatetinydb(Psuedoclientmsg) # json loads in Updatetinydb, sent in bytes
        elif Psuedoclientmsg == "ClientSENDDone":
            print("got ClientSENDDone from paul")
            PsuedoClient.send("pass".encode(FORMAT))
        elif Psuedoclientmsg == "Print Server":
            for row in db:
                print(row)
            PsuedoClient.send("pass".encode(FORMAT))

# ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
# ^^^^ Receiving for initial run with client ^^^^^^^^^
def receive():
    """
    Handles incoming connections and starts threads for the PI, HMI, paul, and sam clients.

    The server will only accept one connection from each of these clients.  If a client with the same
    nickname is already connected, the server will not accept the new connection.  The server will
    send a message to the client saying "Connected to server!" after accepting the connection.  The
    server will then start a thread for the client, and send a message to the client saying "pass".
    """
    print("Receive in loop")
    PIRunningb, HMIRunningb, paulRunningb = False, False, False # start threads once
    while True:
        # Accept Connection
        time.sleep(0.050)

        client, address = server.accept()
        print("Connected with {}".format(str(address)))

        # Request And Store Nickname
        client.send('NICK'.encode(FORMAT))
        print("I just sent: NICK")
        try:
            nickname = client.recv(1024).decode(FORMAT).strip()  # Add strip() to remove whitespace
        except SocketError as err:
            if err.errno != errno.ECONNRESET: raise
            client.close()
            break
        # Print And Broadcast Nickname
        print("Nickname is {}".format(nickname))
        if nickname == b"pass": pass
        #broadcast("{} joined!".format(nickname).encode('FORMAT'))
        # Start Handling Threads For Clients, only handle these 4 clients
        if nickname == "PI": # nickname and prevent multi instances
            if not PIRunningb:
                clientPI = client
                clientPI.send('Connected to server!'.encode(FORMAT))
                handlePI_thread = threading.Thread(target=handlePI, args=(clientPI,), daemon=True)
                time.sleep(0.100)
                clientPI.send('pass'.encode(FORMAT))
                handlePI_thread.start()
            PIRunningb = True # flag to prevent multi instances
        elif nickname == "HMI": # nickname and prevent multi instances
            clientHMI = client
            if not HMIRunningb:
                clientHMI.send('Connected to server!'.encode(FORMAT))
                handleHMI_thread = threading.Thread(target=handleHMI, args=(clientHMI,),daemon=True)
                time.sleep(0.100)
                clientHMI.send('pass'.encode(FORMAT))
                handleHMI_thread.start()
            HMIRunningb = True
        elif nickname == "paul": # nickname and prevent multi instances
            clientpaul = client
            if not paulRunningb:
                clientPI = client
                clientpaul.send('Connected to server!'.encode(FORMAT))
                time.sleep(0.100)
                clientpaul.send('pass'.encode(FORMAT))
                handlepaul_thread = threading.Thread(target=handlepaul, args=(clientpaul,),daemon=True)
                handlepaul_thread.start()
            paulRunningb = True
        elif nickname == "sam":
            pass
        else:
            print("Client not found!")
            print(nickname)

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
    print("In ClientgetDBUpdate")
    try:
        #for i in range(81):
        #temp1=db.search(query["HMI_READi"] == Xstatus)
        if db.search(query["HMI_READi"] == Xstatus):
            temp1.append(db.search(query["HMI_READi"] == Xstatus))
            ToUpdate = json.dumps(temp1)
    except IndexError:
        print("ClientGetDBUpdate Exception! lie 534")
        pass
    try:
        if ToUpdate == []: pass  # if =none then set to blank
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
    print("ToUpdateDB for json_loads: ", ToUpdateDB)
    json_data = [] # clear register
    if not ToUpdateDB or not ToUpdateDB.strip():
        return
    s = ToUpdateDB.lstrip()
    if not (s.startswith("{") or s.startswith("[")):
        print(f"[WARN] Skipping non-JSON payload: {ToUpdateDB[:200]}")
        return

    # Parse and update DB; override HMI_READi to 0 to indicate server accepted the update
    try:
        json_data = json.loads(ToUpdateDB)
        # Ensure we handle a single object or a list
        if isinstance(json_data, dict):
            json_data = [json_data]
        for item in json_data:
            Index = item.get("INDEX")
            if Index is None:
                continue
            tag = item.get("TAG")
            HMI_Valuei = item.get("HMI_VALUEi")
            HMI_Valueb = item.get("HMI_VALUEb")
            PI_Valuef = item.get("PI_VALUEf")
            PI_Valueb = item.get("PI_VALUEb")
            # Force HMI_READi cleared on server accept
            db.update({
                "HMI_VALUEi": HMI_Valuei,
                "HMI_VALUEb": HMI_Valueb,
                "PI_VALUEf": PI_Valuef,
                "PI_VALUEb": PI_Valueb,
                "HMI_READi": 0
            }, query.INDEX == Index)
            print("update done for INDEX", Index, "TAG=", tag)

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
                        print(f"[Mirror] Updated main tag {main_tag} PI_VALUEb={new_state} (from {tag})")
                    else:
                        print(f"[Mirror] Main tag {main_tag} not found to mirror from {tag}")
    except Exception as e:
        print("[ERROR] Failed to parse/apply JSON from HMI:", e)
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
    for j in range(1,3):
        for i in range(len(dbRows1)):
            Index = dbRows1[i].get("INDEX", "Not Found")
            print(Index)
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
print("db count: ", db.count(query.HMI_READi == 0))
if db.count(all) < 1: # is disk db empty?
    LoadDB()
    print("Server Started & created DB")
elif db.count(all)>80:
    print("Server Started & DB corrupted resetting")
    db.truncate()
    LoadDB()
    print("DB now at: ", db.count(all))

receive_thread = threading.Thread(target=receive,)
receive_thread.start()
