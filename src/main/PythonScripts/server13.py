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
import threading
import time
# from json import loads as json_loads
from json import dumps as json_dumps, loads as json_loads
# from threading import Event
from tinydb import TinyDB, Query
from tinydb.middlewares import CachingMiddleware
from tinydb.storages import JSONStorage

# Connection Data
HOST = '127.0.0.1'
PORT = 55555
FORMAT = "utf-8"

global PIstatus, HMIstatus, SeverRdyb, db, SaveDBb
PIstatus = "PINo"  # other is "PIYes"
HMIstatus = "HMINo"
ServerRdyb = False

SeverRdyb = False

db = TinyDB('DBHMItoPI.json', storage=CachingMiddleware(JSONStorage))
#CachingMiddleware.WRITE_CACHE_SIZE = 1000 writes

# Starting Server
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#allow reuse of address
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind((HOST, PORT))
server.listen(4)  # max cients is 4
Xstatus = 2
# Lists For Clients and Their Nicknames

query = Query()  # query object


def LoadDB():
    db.insert({"INDEX": 1, "TAG": "HMI_RHT", "HMI_VALUEi": 25, "HMI_VALUEb": False, "PI_VALUEf": 0.0, "PI_VALUEb": None,
               "HMI_READi": 1})
    db.insert({"INDEX": 2, "TAG": "HMI_TramStopTime", "HMI_VALUEi": 10, "HMI_VALUEb": True, "PI_VALUEf": 0.0,
               "PI_VALUEb": None, "HMI_READi": 0})
    db.insert(
        {"INDEX": 3, "TAG": "HMI_AllQuietb", "HMI_VALUEi": 0, "HMI_VALUEb": False, "PI_VALUEf": 0.0, "PI_VALUEb": None,
         "HMI_READi": 1})
    db.insert(
        {"INDEX": 4, "TAG": "HMI_LIGHTONOFFb", "HMI_VALUEi": 0, "HMI_VALUEb": True, "PI_VALUEf": 0.0, "PI_VALUEb": None,
         "HMI_READi": 0})
    db.insert({"INDEX": 5, "TAG": "HMI_RR2_RR3Pwrb", "HMI_VALUEi": 0, "HMI_VALUEb": False, "PI_VALUEf": 0.0,
               "PI_VALUEb": None, "HMI_READi": 1})
    db.insert(
        {"INDEX": 6, "TAG": "HMI_RRBellb", "HMI_VALUEi": 0, "HMI_VALUEb": True, "PI_VALUEf": 0.0, "PI_VALUEb": None,
         "HMI_READi": 0})
    db.insert({"INDEX": 7, "TAG": "HMI_RRDieselSteamb", "HMI_VALUEi": 0, "HMI_VALUEb": False, "PI_VALUEf": 0.0,
               "PI_VALUEb": None, "HMI_READi": 0})
    db.insert(
        {"INDEX": 8, "TAG": "HMI_RRHornb", "HMI_VALUEi": 0, "HMI_VALUEb": True, "PI_VALUEf": 0.0, "PI_VALUEb": None,
         "HMI_READi": 0})
    db.insert(
        {"INDEX": 9, "TAG": "HMI_RRQuietb", "HMI_VALUEi": 0, "HMI_VALUEb": False, "PI_VALUEf": 0.0, "PI_VALUEb": None,
         "HMI_READi": 2})
    db.insert(
        {"INDEX": 10, "TAG": "HMI_RRWhistleb", "HMI_VALUEi": 0, "HMI_VALUEb": True, "PI_VALUEf": 0.0, "PI_VALUEb": None,
         "HMI_READi": 2})
    db.insert(
        {"INDEX": 11, "TAG": "HMI_Switch1ABb", "HMI_VALUEi": 0, "HMI_VALUEb": True, "PI_VALUEf": 0.0, "PI_VALUEb": None,
         "HMI_READi": 2})
    db.insert({"INDEX": 12, "TAG": "HMI_Switch2RR3b", "HMI_VALUEi": 0, "HMI_VALUEb": True, "PI_VALUEf": 0.0,
               "PI_VALUEb": None, "HMI_READi": 2})
    db.insert({"INDEX": 13, "TAG": "HMI_Switch3RR4b", "HMI_VALUEi": 0, "HMI_VALUEb": False, "PI_VALUEf": 0.0,
               "PI_VALUEb": None, "HMI_READi": 0})
    db.insert({"INDEX": 14, "TAG": "HMI_Switch4RR3b", "HMI_VALUEi": 0, "HMI_VALUEb": True, "PI_VALUEf": 0.0,
               "PI_VALUEb": None, "HMI_READi": 0})
    db.insert({"INDEX": 15, "TAG": "HMI_Switch5ABb", "HMI_VALUEi": 0, "HMI_VALUEb": False, "PI_VALUEf": 0.0,
               "PI_VALUEb": None, "HMI_READi": 0})
    db.insert(
        {"INDEX": 16, "TAG": "HMI_Switch6ABb", "HMI_VALUEi": 0, "HMI_VALUEb": True, "PI_VALUEf": 0.0, "PI_VALUEb": None,
         "HMI_READi": 0})
    db.insert(
        {"INDEX": 17, "TAG": "HMI_TramQuietb", "HMI_VALUEi": 0, "HMI_VALUEb": True, "PI_VALUEf": 0.0, "PI_VALUEb": None,
         "HMI_READi": 0})
    db.insert({"INDEX": 18, "TAG": "HMI_TramStpStn_2b", "HMI_VALUEi": 0, "HMI_VALUEb": True, "PI_VALUEf": 0.0,
               "PI_VALUEb": None, "HMI_READi": 0})
    db.insert({"INDEX": 19, "TAG": "HMI_TramStpStn_3b", "HMI_VALUEi": 0, "HMI_VALUEb": False, "PI_VALUEf": 0.0,
               "PI_VALUEb": None, "HMI_READi": 0})
    db.insert({"INDEX": 20, "TAG": "HMI_TramStpStn_5b", "HMI_VALUEi": 0, "HMI_VALUEb": True, "PI_VALUEf": 0.0,
               "PI_VALUEb": None, "HMI_READi": 0})
    db.insert({"INDEX": 21, "TAG": "HMI_TramStpStn_6b", "HMI_VALUEi": 0, "HMI_VALUEb": False, "PI_VALUEf": 0.0,
               "PI_VALUEb": None, "HMI_READi": 0})
    db.insert(
        {"INDEX": 22, "TAG": "HMI_Future_1", "HMI_VALUEi": 0, "HMI_VALUEb": True, "PI_VALUEf": 0.0, "PI_VALUEb": None,
         "HMI_READi": 0})
    db.insert(
        {"INDEX": 23, "TAG": "HMI_Future_2", "HMI_VALUEi": 0, "HMI_VALUEb": True, "PI_VALUEf": 0.0, "PI_VALUEb": None,
         "HMI_READi": 0})
    db.insert(
        {"INDEX": 24, "TAG": "HMI_Future_3", "HMI_VALUEi": 0, "HMI_VALUEb": True, "PI_VALUEf": 0.0, "PI_VALUEb": None,
         "HMI_READi": 0})
    db.insert(
        {"INDEX": 25, "TAG": "HMI_Future_4", "HMI_VALUEi": 0, "HMI_VALUEb": True, "PI_VALUEf": 0.0, "PI_VALUEb": None,
         "HMI_READi": 0})
    db.insert(
        {"INDEX": 26, "TAG": "HMI_Future_5", "HMI_VALUEi": 0, "HMI_VALUEb": True, "PI_VALUEf": 0.0, "PI_VALUEb": None,
         "HMI_READi": 0})
    db.insert(
        {"INDEX": 27, "TAG": "HMI_Future_6", "HMI_VALUEi": 0, "HMI_VALUEb": True, "PI_VALUEf": 0.0, "PI_VALUEb": None,
         "HMI_READi": 0})
    db.insert(
        {"INDEX": 28, "TAG": "HMI_Future_7", "HMI_VALUEi": 0, "HMI_VALUEb": True, "PI_VALUEf": 0.0, "PI_VALUEb": None,
         "HMI_READi": 0})
    db.insert(
        {"INDEX": 29, "TAG": "HMI_Future_8", "HMI_VALUEi": 0, "HMI_VALUEb": True, "PI_VALUEf": 0.0, "PI_VALUEb": None,
         "HMI_READi": 0})
    db.insert(
        {"INDEX": 30, "TAG": "HMI_Future_9", "HMI_VALUEi": 0, "HMI_VALUEb": True, "PI_VALUEf": 0.0, "PI_VALUEb": None,
         "HMI_READi": 0})
    db.insert(
        {"INDEX": 31, "TAG": "HMI_Future_10", "HMI_VALUEi": 0, "HMI_VALUEb": True, "PI_VALUEf": 0.0, "PI_VALUEb": None,
         "HMI_READi": 0})
    db.insert(
        {"INDEX": 32, "TAG": "HMI_Future_11", "HMI_VALUEi": 0, "HMI_VALUEb": True, "PI_VALUEf": 0.0, "PI_VALUEb": None,
         "HMI_READi": 0})
    db.insert(
        {"INDEX": 33, "TAG": "HMI_Future_12", "HMI_VALUEi": 0, "HMI_VALUEb": True, "PI_VALUEf": 0.0, "PI_VALUEb": None,
         "HMI_READi": 0})
    db.insert(
        {"INDEX": 34, "TAG": "HMI_Future_13", "HMI_VALUEi": 0, "HMI_VALUEb": True, "PI_VALUEf": 0.0, "PI_VALUEb": None,
         "HMI_READi": 0})
    db.insert(
        {"INDEX": 35, "TAG": "HMI_Future_14", "HMI_VALUEi": 0, "HMI_VALUEb": True, "PI_VALUEf": 0.0, "PI_VALUEb": None,
         "HMI_READi": 0})
    db.insert(
        {"INDEX": 36, "TAG": "HMI_Future_15", "HMI_VALUEi": 0, "HMI_VALUEb": True, "PI_VALUEf": 0.0, "PI_VALUEb": None,
         "HMI_READi": 0})
    db.insert(
        {"INDEX": 37, "TAG": "HMI_Future_16", "HMI_VALUEi": 0, "HMI_VALUEb": True, "PI_VALUEf": 0.0, "PI_VALUEb": None,
         "HMI_READi": 0})
    db.insert(
        {"INDEX": 38, "TAG": "HMI_Future_17", "HMI_VALUEi": 0, "HMI_VALUEb": True, "PI_VALUEf": 0.0, "PI_VALUEb": None,
         "HMI_READi": 0})
    db.insert(
        {"INDEX": 39, "TAG": "HMI_Future_18", "HMI_VALUEi": 0, "HMI_VALUEb": True, "PI_VALUEf": 0.0, "PI_VALUEb": None,
         "HMI_READi": 0})
    db.insert(
        {"INDEX": 40, "TAG": "HMI_Future_19", "HMI_VALUEi": 0, "HMI_VALUEb": True, "PI_VALUEf": 0.0, "PI_VALUEb": None,
         "HMI_READi": 0})
    db.insert(
        {"INDEX": 41, "TAG": "HMI_Future_20", "HMI_VALUEi": 0, "HMI_VALUEb": True, "PI_VALUEf": 0.0, "PI_VALUEb": None,
         "HMI_READi": 0})
    db.insert(
        {"INDEX": 42, "TAG": "HMI_Future_21", "HMI_VALUEi": 0, "HMI_VALUEb": True, "PI_VALUEf": 0.0, "PI_VALUEb": None,
         "HMI_READi": 0})
    db.insert(
        {"INDEX": 43, "TAG": "HMI_Future_22", "HMI_VALUEi": 0, "HMI_VALUEb": True, "PI_VALUEf": 0.0, "PI_VALUEb": None,
         "HMI_READi": 0})
    db.insert(
        {"INDEX": 44, "TAG": "HMI_Future_23", "HMI_VALUEi": 0, "HMI_VALUEb": True, "PI_VALUEf": 0.0, "PI_VALUEb": None,
         "HMI_READi": 0})
    db.insert(
        {"INDEX": 45, "TAG": "HMI_Future_24", "HMI_VALUEi": 0, "HMI_VALUEb": True, "PI_VALUEf": 0.0, "PI_VALUEb": None,
         "HMI_READi": 0})
    db.insert(
        {"INDEX": 46, "TAG": "HMI_Future_25", "HMI_VALUEi": 0, "HMI_VALUEb": True, "PI_VALUEf": 0.0, "PI_VALUEb": None,
         "HMI_READi": 0})
    db.insert(
        {"INDEX": 47, "TAG": "HMI_Future_26", "HMI_VALUEi": 0, "HMI_VALUEb": True, "PI_VALUEf": 0.0, "PI_VALUEb": None,
         "HMI_READi": 0})
    db.insert(
        {"INDEX": 48, "TAG": "HMI_Future_27", "HMI_VALUEi": 0, "HMI_VALUEb": True, "PI_VALUEf": 0.0, "PI_VALUEb": None,
         "HMI_READi": 0})
    db.insert(
        {"INDEX": 49, "TAG": "HMI_Future_28", "HMI_VALUEi": 0, "HMI_VALUEb": True, "PI_VALUEf": 0.0, "PI_VALUEb": None,
         "HMI_READi": 0})
    db.insert({"INDEX": 50, "TAG": "RR1ABspeed_HMI", "HMI_VALUEi": 0, "HMI_VALUEb": None, "PI_VALUEf": 0.12,
               "PI_VALUEb": None, "HMI_READi": 0})
    db.insert({"INDEX": 51, "TAG": "RR1CDspeed_HMI", "HMI_VALUEi": 0, "HMI_VALUEb": None, "PI_VALUEf": 0.12,
               "PI_VALUEb": None, "HMI_READi": 0})
    db.insert({"INDEX": 52, "TAG": "RR2ABspeed_HMI", "HMI_VALUEi": 0, "HMI_VALUEb": None, "PI_VALUEf": 0.12,
               "PI_VALUEb": None, "HMI_READi": 0})
    db.insert({"INDEX": 53, "TAG": "Switch1Main_HMIb", "HMI_VALUEi": 0, "HMI_VALUEb": None, "PI_VALUEf": 0.12,
               "PI_VALUEb": False, "HMI_READi": 0})
    db.insert({"INDEX": 54, "TAG": "open", "HMI_VALUEi": 0, "HMI_VALUEb": None, "PI_VALUEf": 0.12, "PI_VALUEb": False,
               "HMI_READi": 0})
    db.insert({"INDEX": 55, "TAG": "Switch2RR3Main_HMIb", "HMI_VALUEi": 0, "HMI_VALUEb": None, "PI_VALUEf": 0.12,
               "PI_VALUEb": False, "HMI_READi": 0})
    db.insert({"INDEX": 56, "TAG": "open", "HMI_VALUEi": 0, "HMI_VALUEb": None, "PI_VALUEf": 0.12, "PI_VALUEb": False,
               "HMI_READi": 0})
    db.insert({"INDEX": 57, "TAG": "Switch3RR4Main_HMIb", "HMI_VALUEiy": 0, "HMI_VALUEb": None, "PI_VALUEf": 0.12,
               "PI_VALUEb": True, "HMI_READi": 0})
    db.insert({"INDEX": 58, "TAG": "open", "HMI_VALUEi": 0, "HMI_VALUEb": None, "PI_VALUEf": 0.12, "PI_VALUEb": False,
               "HMI_READi": 0})
    db.insert({"INDEX": 59, "TAG": "Switch4RR3Main_HMIb", "HMI_VALUEi": 0, "HMI_VALUEb": None, "PI_VALUEf": 0.12,
               "PI_VALUEb": False, "HMI_READi": 0})
    db.insert({"INDEX": 60, "TAG": "open", "HMI_VALUEi": 0, "HMI_VALUEb": None, "PI_VALUEf": 0.12, "PI_VALUEb": False,
               "HMI_READi": 0})
    db.insert({"INDEX": 61, "TAG": "Switch5Main_HMIb", "HMI_VALUEi": 0, "HMI_VALUEb": None, "PI_VALUEf": 0.12,
               "PI_VALUEb": False, "HMI_READi": 0})
    db.insert({"INDEX": 62, "TAG": "open", "HMI_VALUEi": 0, "HMI_VALUEb": None, "PI_VALUEf": 0.12, "PI_VALUEb": True,
               "HMI_READi": 0})
    db.insert({"INDEX": 63, "TAG": "Switch6Main_HMIb", "HMI_VALUEi": 0, "HMI_VALUEb": None, "PI_VALUEf": 0.12,
               "PI_VALUEb": False, "HMI_READi": 0})
    db.insert({"INDEX": 64, "TAG": "RR2orRR3Pwr_HMIb", "HMI_VALUEi": 0, "HMI_VALUEb": None, "PI_VALUEf": 0.12,
               "PI_VALUEb": False, "HMI_READi": 0})
    db.insert({"INDEX": 65, "TAG": "TramStn1_HMIb", "HMI_VALUEi": 0, "HMI_VALUEb": None, "PI_VALUEf": 0.12,
               "PI_VALUEb": False, "HMI_READi": 0})
    db.insert({"INDEX": 66, "TAG": "TramStn2_HMIb", "HMI_VALUEi": 0, "HMI_VALUEb": None, "PI_VALUEf": 0.12,
               "PI_VALUEb": False, "HMI_READi": 0})
    db.insert({"INDEX": 67, "TAG": "TramStn3_HMIb", "HMI_VALUEi": 0, "HMI_VALUEb": None, "PI_VALUEf": 0.12,
               "PI_VALUEb": False, "HMI_READi": 0})
    db.insert(
        {"INDEX": 68, "TAG": "TramStn4_HMIb", "HMI_VALUEi": 0, "HMI_VALUEb": None, "PI_VALUEf": 0.12, "PI_VALUEb": True,
         "HMI_READi": 0})
    db.insert({"INDEX": 69, "TAG": "TramStn5_HMIb", "HMI_VALUEi": 0, "HMI_VALUEb": None, "PI_VALUEf": 0.12,
               "PI_VALUEb": False, "HMI_READi": 0})
    db.insert({"INDEX": 70, "TAG": "TramStn6_HMIb", "HMI_VALUEi": 0, "HMI_VALUEb": None, "PI_VALUEf": 0.12,
               "PI_VALUEb": False, "HMI_READi": 0})
    db.insert(
        {"INDEX": 71, "TAG": "PI_Future_1", "HMI_VALUEi": 0, "HMI_VALUEb": None, "PI_VALUEf": 0.12, "PI_VALUEb": False,
         "HMI_READi": 0})
    db.insert(
        {"INDEX": 72, "TAG": "PI_Future_2", "HMI_VALUEi": 0, "HMI_VALUEb": None, "PI_VALUEf": 0.12, "PI_VALUEb": False,
         "HMI_READi": 0})
    db.insert(
        {"INDEX": 73, "TAG": "PI_Future_3", "HMI_VALUEi": 0, "HMI_VALUEb": None, "PI_VALUEf": 0.12, "PI_VALUEb": False,
         "HMI_READi": 0})
    db.insert(
        {"INDEX": 74, "TAG": "PI_Future_4", "HMI_VALUEi": 0, "HMI_VALUEb": None, "PI_VALUEf": 0.12, "PI_VALUEb": False,
         "HMI_READi": 0})
    db.insert(
        {"INDEX": 75, "TAG": "PI_Future_5", "HMI_VALUEi": 0, "HMI_VALUEb": None, "PI_VALUEf": 0.12, "PI_VALUEb": False,
         "HMI_READi": 0})
    db.insert(
        {"INDEX": 76, "TAG": "PI_Future_6", "HMI_VALUEi": 0, "HMI_VALUEb": None, "PI_VALUEf": 0.12, "PI_VALUEb": False,
         "HMI_READi": 0})
    db.insert(
        {"INDEX": 77, "TAG": "PI_Future_6", "HMI_VALUEi": 0, "HMI_VALUEb": None, "PI_VALUEf": 0.12, "PI_VALUEb": False,
         "HMI_READi": 0})
    db.insert(
        {"INDEX": 78, "TAG": "PI_Future_8", "HMI_VALUEi": 0, "HMI_VALUEb": None, "PI_VALUEf": 0.12, "PI_VALUEb": False,
         "HMI_READi": 0})
    db.insert(
        {"INDEX": 79, "TAG": "PI_Future_9", "HMI_VALUEi": 0, "HMI_VALUEb": None, "PI_VALUEf": 0.12, "PI_VALUEb": False,
         "HMI_READi": 0})
    db.insert(
        {"INDEX": 80, "TAG": "PI_Future_10", "HMI_VALUEi": 0, "HMI_VALUEb": None, "PI_VALUEf": 0.12, "PI_VALUEb": False,
         "HMI_READi": 0})


# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# Handling Messages From Clients
def handlePI(clientPI):
    global PIstatus, HMIstatus, ServerRdyb, ToUpdate
    Xstatus == 2
    HMIstatus, PIstatus = "HMINo", "PINo"
    PISendEntireb = False
    SendPIupdateb = False
    ServerRdyb = False
    while True:
        time.sleep(0.050)
        try:
            clientmsg = clientPI.recv(12244).decode(FORMAT)
            if clientmsg != "": print("Client msg: ", clientmsg)
        except:
            # Removing And Closing Clients
            clientPI.close()
            break
        # begin to listen for correct keywords for actions
        # set by server to notify if handleHMI changed DB, PIYes or PINo
        if clientmsg == "PINew":
            clientPI.send(PIstatus.encode(FORMAT))

        elif clientmsg == "PISendingUpdate":  # PI is ready to send data
            # Update db from PI and set flag for HMI to get
            ServerRdyb = True
            clientPI.send("ServerReadytoRecv".encode(FORMAT))  # send ready
            time.sleep(0.050)  # give time for PI to send
            clientmsg = clientPI.recv(12288).decode(FORMAT)
            time.sleep(0.050)  # give time for PI to send
            if clientmsg != "PISendingUpdate":  # Got update
                Updatetinydb(clientmsg)
                HMIstatus = "HMIYes"  # inform HMI new updates

        # Sending entire DB as PI ready
        elif clientmsg == "PIReadytoRecv" and PISendEntireb:
            PISendEntireb = False
            clientPI.send(EntireDB.encode(FORMAT))  # sent
            ClearFlagsEntiredb(Xstatus)
            if Xstatus == 1:
                HMIstatus = "HMINo"
            elif Xstatus == 2:
                PIstatus = "PINo"
            print("sent entire DB")

        # Sending only updates from DB as PI ready
        elif clientmsg == "PIReadytoRecv" and SendPIupdateb:
            SendPIupdateb = False
            if ToUpdate != []:
                ToUpdate1 = bytes(str(ToUpdate), FORMAT)  #Query for updates
                clientPI.send(ToUpdate1)  # Send
                ClearFlagsUpdatedb(ToUpdate, Xstatus)
                print("sent update")
            else:
                print("Update is empty")
                clientPI.send("No Update Available".encode(FORMAT))  # sent
            if Xstatus == 1:
                HMIstatus = "HMINo"
            elif Xstatus == 2:
                PIstatus = "PINo"

            #Server to send entire DB
        elif clientmsg == "ServerSendEntiretoPI":  # PI request entire DB
            PISendEntireb = True  # need to wait until PI ready
            EntireDB = json.dumps(db.all())
            print("PISendEntireb: ", PISendEntireb)  # DB now string
            # wait on  PI to say ready

            # Query and prep update for sending to PI
        elif clientmsg == "ServerSendUpdatestoPI":
            print("IN SERVER SEND UPDATE")
            ToUpdate = []
            ToUpdate = ClientgetDBUpdate(Xstatus)
            SendPIupdateb = True
            PISendEntireb = False
            PIstatus = "PINo"  # Sent update
            print("DBUpdates: ", ToUpdate)


# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# Handling Messages From Clients
def handleHMI(clientHMI):
    global PIstatus, HMIstatus, ServerRdyb, ToUpdate
    Xstatus == 1  # This is HMI
    HMIstatus, PIstatus = "HMINo\n", "PINo\n"
    HMISendEntireb = False
    SendHMIupdateb = False
    ServerRdyb = False
    while True:
        time.sleep(0.050)
        try:
            clientmsg = clientHMI.recv(12244).decode(FORMAT)
            if clientmsg != "": print("Client msg: ", clientmsg)
        except:
            # Removing And Closing Clients
            clientHMI.close()
            break
        # begin to listen for correct keywords for actions
        # set by server to notify if handleHMI changed DB, PIYes or PINo
        if clientmsg == "HMINew":
            clientHMI.send(HMIstatus.encode(FORMAT))

        elif clientmsg == "HMISendingUpdate":  # PI is ready to send data
            # Update db from PI and set flag for HMI to get
            ServerRdyb = True
            clientHMI.send("ServerReadytoRecv\n".encode(FORMAT))  # send ready
            time.sleep(0.050)  # give time for PI to send
            clientmsg = clientHMI.recv(12288).decode(FORMAT)
            time.sleep(0.050)  # give time for PI to send
            if clientmsg != "HMISendingUpdate":  # Got update
                Updatetinydb(clientmsg)
                HMIstatus = "PIYes"  # inform HMI new updates

        # Sending entire DB as PI ready
        elif clientmsg == "HMIReadytoRecv" and HMISendEntireb:
            HMISendEntireb = False
            clientHMI.send(EntireDB.encode(FORMAT) + b'\n')  # sent
            ClearFlagsEntiredb(Xstatus)
            if Xstatus == 1:
                HMIstatus = "HMINo"
            elif Xstatus == 2:
                PIstatus = "PINo"
            print("sent entire DB")

        # Sending only updates from DB as PI ready
        elif clientmsg == "HMIReadytoRecv" and SendHMIupdateb:
            SendHMIupdateb = False
            if ToUpdate != []:
                ToUpdate1 = bytes(str(ToUpdate), FORMAT)  #Query for updates
                clientHMI.send(ToUpdate1 + b'\n')  # Send
                ClearFlagsUpdatedb(ToUpdate, Xstatus)
                print("sent update")
            else:
                print("Update is empty")
                clientHMI.send("No Update Available\n".encode(FORMAT))  # sent
            if Xstatus == 1:
                HMIstatus = "HMINo"
            elif Xstatus == 2:
                PIstatus = "PINo"

            #Server to send entire DB
        elif clientmsg == "ServerSendEntiretoHMI":  # PI request entire DB
            HMISendEntireb = True  # need to wait until PI ready
            EntireDB = json.dumps(db.all())
            print("HMISendEntireb: ", HMISendEntireb)  # DB now string
            # wait on  PI to say ready

            # Query and prep update for sending to PI
        elif clientmsg == "ServerSendUpdatestoHMI":
            print("IN SERVER SEND UPDATE")
            ToUpdate = []
            ToUpdate = ClientgetDBUpdate(Xstatus)
            SendHMIupdateb = True
            HMISendEntireb = False
            PIstatus = "HMINo"  # Sent update
            print("DBUpdates: ", ToUpdate)


# ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
# ^^^^ Receiving for initial run with client ^^^^^^^^^
def receive():
    while True:
        # Accept Connection
        client, address = server.accept()
        print("Connected with {}".format(str(address)))

        # Request And Store Nickname
        client.send('NICK\n'.encode(FORMAT))
        print("I just sent: NICK")
        nickname = client.recv(1024).decode(FORMAT)
        # Print And Broadcast Nickname
        print("Nickname is {}".format(nickname))
        #broadcast("{} joined!".format(nickname).encode('FORMAT'))
        client.send('Connected to server!\n'.encode(FORMAT))

        # Start Handling Threads For Clients
        if nickname == "PI":
            clientPI = client
            handlePI_thread = threading.Thread(target=handlePI, args=(clientPI,))
            handlePI_thread.start()
        elif nickname == "HMI":
            clientHMI = client
            handleHMI_thread = threading.Thread(target=handleHMI, args=(clientHMI,))
            handleHMI_thread.start()
        else:
            print("Client not found!")
            print(bytes(nickname, FORMAT))
        # only handle these 2 clients


#   ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
# SERVER PROVIDES UPDATES TO CLIENTS
def ClientgetDBUpdate(Xstatus):
    temp1 = []
    print("In ClientgetDBUpdate")
    try:
        #for i in range(81):
        #temp1=db.search(query["HMI_READi"] == Xstatus)
        if db.search(query["HMI_READi"] == Xstatus):
            temp1.append(db.search(query["HMI_READi"] == Xstatus))
            ToUpdate = json.dumps(temp1)
        for row in ToUpdate:
            print(row)
    except IndexError:
        print("ClientGetDBUpdate Exception! lie 334")
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
    print("In Updatetinydb")
    print("type of what sent: ", type(ToUpdateDB))
    print("length of sent: ", len(ToUpdateDB))
    json_data = json.loads(ToUpdateDB)
    #json_data = ToUpdateDB
    print("json loads done:")
    for i in range(len(json_data[0])):
        Index = json_data[0][i].get("INDEX")
        HMI_Valuei = json_data[0][i].get("HMI_VALUEi")
        HMI_Valueb = json_data[0][i].get("HMI_VALUEb")
        PI_Valuef = json_data[0][i].get("PI_VALUEf")
        PI_Valueb = json_data[0][i].get("PI_VALUEb")
        HMI_Readi = json_data[0][i].get("HMI_READi")
        #db.update({"HMI_READi": 0}, query.INDEX == Index)
        db.update({"HMI_VALUEi": HMI_Valuei}, query.INDEX == Index)
        db.update({"HMI_VALUEb": HMI_Valueb}, query.INDEX == Index)
        db.update({"PI_VALUEf": PI_Valuef}, query.INDEX == Index)
        db.update({"PI_VALUEb": PI_Valueb}, query.INDEX == Index)
        db.update({"HMI_READi": HMI_Readi}, query.INDEX == Index)
    print("update done")
    db.storage.flush()  # save
    return


#   ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
# CLEAR SEND FLAGS IN TINY DB from either
#^^^^^^^^^ CLEAR FLAGS TINY DB ^^^^^^^^^^^
def ClearFlagsUpdatedb(dbRows, Xstatus):
    global HMIstatus, PIstatus
    dbRows1 = json_loads(dbRows)
    for i in range(len(dbRows1[0])):
        Index = dbRows1[0][i].get("INDEX", "Not Found")
        print(Index)
        db.update({"HMI_READi": 0}, query.INDEX == Index and query.HMI_READi == Xstatus)
    db.storage.flush()  # save
    for row in db:
        print(row)
    # Set Flags for client notification
    if Xstatus == 1:
        HMIstatus = "HMINo"
    elif Xstatus == 2:
        PIstatus = "PINo"


# ^^^^^^^^^^^^^^^^^^
# clear flags, entire db
def ClearFlagsEntiredb(Xstatus):
    print("Xstatus: ", Xstatus)
    db.update({"HMI_READi": 0}, query.HMI_READi == Xstatus)
    db.storage.flush()  # save
    if Xstatus == 1:
        junk = "HMI"
    elif Xstatus == 2:
        junk = "PI"
    print("Set HMI_READi in entire DB to 0 for ", junk)
    print("DB after entire clear")
    for row in db:
        print(row)
    return


# *************************************************************
#****************************MAIN FUNCTION*********************
LoadDB()
print("Server Started")
receive()
