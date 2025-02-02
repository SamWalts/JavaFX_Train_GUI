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
            #print(db.count(query.HMI_READi == 2))      #check db & answer
            if db.count(query.HMI_READi == 2) > 0: clientPI.sendall("PIYes".encode(FORMAT))
            else: clientPI.send("PINo".encode(FORMAT)) # no updates
            #time.sleep(0.100)
        elif PIclientmsg == "ReadytoRecv": # waiting
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
    global HMIstatus, ToUpdate
    print("HMI handle started")
    clientHMI.send("TEST\n".encode(FORMAT))
    while True:
        time.sleep(0.050)   # give other things time
        clientHMImsg = clientHMI.recv(12244).decode(FORMAT)
        print("clientHMImsg at top: ", clientHMImsg)
        if clientHMImsg == "HMINew":    # HMI asking if new data available
            temp = db.count(query.HMI_READi != 0) # search for non '0' values
            print("temp: ", temp)   # print data pulled from server DB
            if temp > 0:
                HMIstatus = "HMIYes \n"
                clientHMI.send(HMIstatus.encode(FORMAT)) # send status to SERVER
                if clientHMImsg == "HMIReadytoRecv":
                    time.sleep(0.050)
                if clientHMImsg == "HMIReadytoRecv":
                    HMIClientdata = db.search(query.HMI_READi != 2) # get local updates
                    HMIjson_data = json.dumps(HMIClientdata)
                    HMIjson_data = bytes(str(HMIjson_data), FORMAT) + bytes("\n", FORMAT) # send new line
                    clientHMI.sendall(HMIjson_data)  # Send updates to HMI
                    print("sent update to HMI")
                    for row in HMIClientdata: #set HMI_READi=0
                        Index = db[row].get("INDEX", "Not Found")
                        db.update({"HMI_READi": 0}, query.INDEX == Index)
                        print("reset HMI_READi's after HMI send")
            else:
                HMIstatus = "HMINo \n"
                clientHMI.send(HMIstatus.encode(FORMAT)) # send status to SERVER

        elif clientHMImsg=="HMIDone":
            clientHMI.send("HMINo \n".encode(FORMAT)) # send status to SERVER

        elif clientHMImsg == "HMISendingUpdate":  # HMI send data
            message ="ServerReadytoRecv \n"
            clientHMI.send(message.encode(FORMAT))
            if clientHMImsg != "HMISendingUpdate": # client sent new string of data
                print("clientHMImsg b4 send to updatetinydb: ", clientHMImsg)
                Updatetinydb(clientHMImsg) # json loads in Updatetinydb, sent in bytes
                clientHMI.send("ServerDone \n".encode(FORMAT)) # send status to HMI
        # DEBUGGING purposes.  Print out the database inside of the Server File.
        elif clientHMImsg == "Print Server":
            for row in db:
                print(row)
            clientHMI.send("pass/n".encode(FORMAT))
# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
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
            PsuedoClient.send("ServerReady".encode(FORMAT))
        elif Psuedoclientmsg.find("INDEX") >= 0: # waiting on data
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
            nickname = client.recv(1024).decode(FORMAT)
        except SocketError as err:
            if err.errno != errno.ECONNRESET: raise # if not connection reset by client then raise
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
def Updatetinydb(ToUpdateDB):  #ToUpdateDB is a nested list
    """
    Updatetinydb updates the tinydb database with the given nested list of json data.

    Parameters:
    ToUpdateDB (list): A nested list of json data to be written to the database.

    Returns:
    None
    """
    print("ToUpdateDB for json_loads: ", ToUpdateDB)
    #ToUpdateDB.find('[{"INDEX"')
    #anyleading = ToUpdateDB.find("[{'INDEX'")
    #print("anyleading: ", anyleading)
    #if anyleading == -1:
    #    print("UpdatetinyDB not found [{INDEX")
    #    return
    #if anyleading > 0:
    #    ToUpdateDB1=ToUpdateDB[:0] + ToUpdateDB[anyleading:] #remove from char index 0 to anyleading
    #print("ToUpdateDB after cleaning: ", ToUpdateDB)
    json_data = [] # clear register
    if ToUpdateDB == "[]" or ToUpdateDB == "pass":
        print("ToUpdateDB is empty!!")
        return
    ToUpdateDB = str(ToUpdateDB)  # ToUpdateDB.decode(FORMAT) FORMAT is default
    ToUpdateDB.replace("'", '"')
    if ToUpdateDB != "[]" or ToUpdateDB != "pass":
        json_data = json.loads(ToUpdateDB)
        for i in range(len(json_data)):
            Index = json_data[i].get("INDEX")
            HMI_Valuei = json_data[i].get("HMI_VALUEi")
            HMI_Valueb = json_data[i].get("HMI_VALUEb")
            PI_Valuef = json_data[i].get("PI_VALUEf")
            PI_Valueb = json_data[i].get("PI_VALUEb")
            HMI_Readi = json_data[i].get("HMI_READi")
            db.update({"HMI_VALUEi": HMI_Valuei, "HMI_VALUEb": HMI_Valueb, "PI_VALUEf": PI_Valuef, "PI_VALUEb": PI_Valueb, "HMI_READi": HMI_Readi}, query.INDEX == Index)
            print("update done")
    else: print("ToUpdateDB is empty")
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
