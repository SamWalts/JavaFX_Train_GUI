''' **************************** PI CLIENT ***************************
*****************************USING TINYDB HERE ******************* '''
import socket
import threading
import time
import json
from json import dumps as json_dumps, loads as json_loads
from tinydb import TinyDB, Query, where
from tinydb.storages import JSONStorage
from tinydb.middlewares import CachingMiddleware
from tinydb_smartcache import SmartCacheTable
query = Query()  # tinydb query object

FORMAT = "utf-8"
# Nickname
NICKNAME = "PI" # UPDATE FOR CLIENT
if NICKNAME == "PI": Xsend = 1  #PI uses 1 to notify HMI
else: Xsend = 2                 # HMI used 2 to notify PI

global ServersendingUpdatesb, ServertoSendb, svrmsg
ServersendingUpdatesb = False
ServertoSendb = False

HMI_Valuei = 0  # Hold HMI value
HMI_Valueb = False  # Hold HMI value
message = []    # holds message to send to server

global PIdb
PIdb = TinyDB('PIDB.json') # Name of DataBase
PIdb.table_class = SmartCacheTable

def Connection(Connectionb):
    for i in range(20):
        if not Connectionb:
            time.sleep(1.000)
            try:
                client.connect(('127.0.0.1', 55555))
                Connectionb = True
            except:
                print("\nSTART SERVER!, CHECK every 1 sec for ", 20-i, " sec")
                time.sleep(1.000)
                Connectionb = False
        else: return Connectionb

# Connecting To the Server
Connectionb = False
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
if not Connectionb:
    Connectionb = Connection(Connectionb) #client.connect(('127.0.0.1', 55555))

def LoadDB():
    PIdb.insert({"INDEX": 1, "TAG":"HMI_RHT", "HMI_VALUEi": 25, "HMI_VALUEb": False, "PI_VALUEf": 0.0, "PI_VALUEb": None, "HMI_READi": 1})
    PIdb.insert({"INDEX": 2, "TAG":"HMI_TramStopTime", "HMI_VALUEi": 10,"HMI_VALUEb":True, "PI_VALUEf": 0.0, "PI_VALUEb": None, "HMI_READi": 0})
    PIdb.insert({"INDEX": 3, "TAG":"HMI_AllQuietb", "HMI_VALUEi": 0, "HMI_VALUEb": False, "PI_VALUEf": 0.0, "PI_VALUEb": None, "HMI_READi": 1})
    PIdb.insert({"INDEX": 4, "TAG":"HMI_LIGHTONOFFb", "HMI_VALUEi": 0, "HMI_VALUEb": True, "PI_VALUEf": 0.0, "PI_VALUEb": None, "HMI_READi": 0})
    PIdb.insert({"INDEX": 5, "TAG":"HMI_RR2_RR3Pwrb", "HMI_VALUEi": 0, "HMI_VALUEb": False, "PI_VALUEf": 0.0, "PI_VALUEb": None, "HMI_READi": 1})
    PIdb.insert({"INDEX": 6, "TAG":"HMI_RRBellb", "HMI_VALUEi": 0, "HMI_VALUEb": True, "PI_VALUEf": 0.0, "PI_VALUEb": None, "HMI_READi": 0})
    PIdb.insert({"INDEX": 7, "TAG":"HMI_RRDieselSteamb", "HMI_VALUEi": 0, "HMI_VALUEb": False, "PI_VALUEf": 0.0, "PI_VALUEb": None, "HMI_READi": 0})
    PIdb.insert({"INDEX": 8, "TAG":"HMI_RRHornb", "HMI_VALUEi": 0, "HMI_VALUEb": True, "PI_VALUEf": 0.0, "PI_VALUEb": None, "HMI_READi": 0})
    PIdb.insert({"INDEX": 9, "TAG":"HMI_RRQuietb", "HMI_VALUEi": 0, "HMI_VALUEb": False, "PI_VALUEf": 0.0, "PI_VALUEb": None, "HMI_READi": 2})
    PIdb.insert({"INDEX": 10, "TAG":"HMI_RRWhistleb", "HMI_VALUEi": 0, "HMI_VALUEb": True, "PI_VALUEf": 0.0, "PI_VALUEb": None, "HMI_READi": 2})
    PIdb.insert({"INDEX": 11, "TAG":"HMI_Switch1ABb", "HMI_VALUEi": 0, "HMI_VALUEb": True, "PI_VALUEf": 0.0, "PI_VALUEb": None, "HMI_READi": 2})
    PIdb.insert({"INDEX": 12, "TAG":"HMI_Switch2RR3b", "HMI_VALUEi": 0, "HMI_VALUEb":True, "PI_VALUEf": 0.0, "PI_VALUEb": None, "HMI_READi": 0})
    PIdb.insert({"INDEX": 13, "TAG":"HMI_Switch3RR4b", "HMI_VALUEi": 0, "HMI_VALUEb": False, "PI_VALUEf": 0.0, "PI_VALUEb":None, "HMI_READi": 0})
    PIdb.insert({"INDEX": 14, "TAG":"HMI_Switch4RR3b", "HMI_VALUEi": 0, "HMI_VALUEb": True, "PI_VALUEf": 0.0, "PI_VALUEb": None, "HMI_READi": 0})
    PIdb.insert({"INDEX": 15, "TAG":"HMI_Switch5ABb", "HMI_VALUEi": 0, "HMI_VALUEb": False, "PI_VALUEf": 0.0, "PI_VALUEb": None, "HMI_READi": 0})
    PIdb.insert({"INDEX": 16, "TAG":"HMI_Switch6ABb", "HMI_VALUEi": 0, "HMI_VALUEb": True, "PI_VALUEf": 0.0, "PI_VALUEb": None, "HMI_READi": 0})
    PIdb.insert({"INDEX": 17, "TAG":"HMI_TramQuietb", "HMI_VALUEi": 0, "HMI_VALUEb": True, "PI_VALUEf": 0.0, "PI_VALUEb": None, "HMI_READi": 0})
    PIdb.insert({"INDEX": 18, "TAG":"HMI_TramStpStn_2b", "HMI_VALUEi":0, "HMI_VALUEb": True, "PI_VALUEf": 0.0, "PI_VALUEb":None, "HMI_READi": 0})
    PIdb.insert({"INDEX": 19, "TAG":"HMI_TramStpStn_3b", "HMI_VALUEi": 0, "HMI_VALUEb": False, "PI_VALUEf": 0.0, "PI_VALUEb": None, "HMI_READi": 0})
    PIdb.insert({"INDEX": 20, "TAG":"HMI_TramStpStn_5b", "HMI_VALUEi":0, "HMI_VALUEb": True, "PI_VALUEf": 0.0, "PI_VALUEb":None, "HMI_READi": 0})
    PIdb.insert({"INDEX": 21, "TAG":"HMI_TramStpStn_6b", "HMI_VALUEi": 0, "HMI_VALUEb": False, "PI_VALUEf": 0.0, "PI_VALUEb": None, "HMI_READi": 0})
    PIdb.insert({"INDEX": 22, "TAG":"HMI_Future_1", "HMI_VALUEi": 0, "HMI_VALUEb": True, "PI_VALUEf": 0.0, "PI_VALUEb": None, "HMI_READi": 0})
    PIdb.insert({"INDEX": 23, "TAG":"HMI_Future_2", "HMI_VALUEi": 0, "HMI_VALUEb": True, "PI_VALUEf": 0.0, "PI_VALUEb": None, "HMI_READi": 0})
    PIdb.insert({"INDEX": 24, "TAG":"HMI_Future_3", "HMI_VALUEi": 0, "HMI_VALUEb": True, "PI_VALUEf": 0.0, "PI_VALUEb": None, "HMI_READi": 0})
    PIdb.insert({"INDEX": 25, "TAG":"HMI_Future_4", "HMI_VALUEi": 0, "HMI_VALUEb": True, "PI_VALUEf": 0.0, "PI_VALUEb": None, "HMI_READi": 0})
    PIdb.insert({"INDEX": 26, "TAG":"HMI_Future_5", "HMI_VALUEi": 0, "HMI_VALUEb": True, "PI_VALUEf": 0.0, "PI_VALUEb": None, "HMI_READi": 0})
    PIdb.insert({"INDEX": 27, "TAG":"HMI_Future_6", "HMI_VALUEi": 0, "HMI_VALUEb": True, "PI_VALUEf": 0.0, "PI_VALUEb": None, "HMI_READi": 0})
    PIdb.insert({"INDEX": 28, "TAG":"HMI_Future_7", "HMI_VALUEi": 0, "HMI_VALUEb": True, "PI_VALUEf": 0.0, "PI_VALUEb": None, "HMI_READi": 0})
    PIdb.insert({"INDEX": 29, "TAG":"HMI_Future_8", "HMI_VALUEi": 0, "HMI_VALUEb": True, "PI_VALUEf": 0.0, "PI_VALUEb": None, "HMI_READi": 0})
    PIdb.insert({"INDEX": 30, "TAG":"HMI_Future_9", "HMI_VALUEi": 0, "HMI_VALUEb": True, "PI_VALUEf": 0.0, "PI_VALUEb": None, "HMI_READi": 0})
    PIdb.insert({"INDEX": 31, "TAG":"HMI_Future_10", "HMI_VALUEi": 0, "HMI_VALUEb": True, "PI_VALUEf": 0.0, "PI_VALUEb": None, "HMI_READi": 0})
    PIdb.insert({"INDEX": 32, "TAG":"HMI_Future_11", "HMI_VALUEi": 0, "HMI_VALUEb": True, "PI_VALUEf": 0.0, "PI_VALUEb": None, "HMI_READi": 0})
    PIdb.insert({"INDEX": 33, "TAG":"HMI_Future_12", "HMI_VALUEi": 0, "HMI_VALUEb": True, "PI_VALUEf": 0.0, "PI_VALUEb": None, "HMI_READi": 0})
    PIdb.insert({"INDEX": 34, "TAG":"HMI_Future_13", "HMI_VALUEi": 0, "HMI_VALUEb": True, "PI_VALUEf": 0.0, "PI_VALUEb": None, "HMI_READi": 0})
    PIdb.insert({"INDEX": 35, "TAG":"HMI_Future_14", "HMI_VALUEi": 0, "HMI_VALUEb": True, "PI_VALUEf": 0.0, "PI_VALUEb": None, "HMI_READi": 0})
    PIdb.insert({"INDEX": 36, "TAG":"HMI_Future_15", "HMI_VALUEi": 0, "HMI_VALUEb": True, "PI_VALUEf": 0.0, "PI_VALUEb": None, "HMI_READi": 0})
    PIdb.insert({"INDEX": 37, "TAG":"HMI_Future_16", "HMI_VALUEi": 0, "HMI_VALUEb": True, "PI_VALUEf": 0.0, "PI_VALUEb": None, "HMI_READi": 0})
    PIdb.insert({"INDEX": 38, "TAG":"HMI_Future_17", "HMI_VALUEi": 0, "HMI_VALUEb": True, "PI_VALUEf": 0.0, "PI_VALUEb": None, "HMI_READi": 0})
    PIdb.insert({"INDEX": 39, "TAG":"HMI_Future_18", "HMI_VALUEi": 0, "HMI_VALUEb": True, "PI_VALUEf": 0.0, "PI_VALUEb": None, "HMI_READi": 0})
    PIdb.insert({"INDEX": 40, "TAG":"HMI_Future_19", "HMI_VALUEi": 0, "HMI_VALUEb": True, "PI_VALUEf": 0.0, "PI_VALUEb": None, "HMI_READi": 0})
    PIdb.insert({"INDEX": 41, "TAG":"HMI_Future_20", "HMI_VALUEi": 0, "HMI_VALUEb": True, "PI_VALUEf": 0.0, "PI_VALUEb": None, "HMI_READi": 0})
    PIdb.insert({"INDEX": 42, "TAG":"HMI_Future_21", "HMI_VALUEi": 0, "HMI_VALUEb": True, "PI_VALUEf": 0.0, "PI_VALUEb": None, "HMI_READi": 0})
    PIdb.insert({"INDEX": 43, "TAG":"HMI_Future_22", "HMI_VALUEi": 0, "HMI_VALUEb": True, "PI_VALUEf": 0.0, "PI_VALUEb": None, "HMI_READi": 0})
    PIdb.insert({"INDEX": 44, "TAG":"HMI_Future_23", "HMI_VALUEi": 0, "HMI_VALUEb": True, "PI_VALUEf": 0.0, "PI_VALUEb": None, "HMI_READi": 0})
    PIdb.insert({"INDEX": 45, "TAG":"HMI_Future_24", "HMI_VALUEi": 0, "HMI_VALUEb": True, "PI_VALUEf": 0.0, "PI_VALUEb": None, "HMI_READi": 0})
    PIdb.insert({"INDEX": 46, "TAG":"HMI_Future_25", "HMI_VALUEi": 0, "HMI_VALUEb": True, "PI_VALUEf": 0.0, "PI_VALUEb": None, "HMI_READi": 0})
    PIdb.insert({"INDEX": 47, "TAG":"HMI_Future_26", "HMI_VALUEi": 0, "HMI_VALUEb": True, "PI_VALUEf": 0.0, "PI_VALUEb": None, "HMI_READi": 0})
    PIdb.insert({"INDEX": 48, "TAG":"HMI_Future_27", "HMI_VALUEi": 0, "HMI_VALUEb": True, "PI_VALUEf": 0.0, "PI_VALUEb": None, "HMI_READi": 0})
    PIdb.insert({"INDEX": 49, "TAG":"HMI_Future_28", "HMI_VALUEi": 0, "HMI_VALUEb": True, "PI_VALUEf": 0.0, "PI_VALUEb":None, "HMI_READi": 0})
    PIdb.insert({"INDEX": 50, "TAG":"RR1ABspeed_HMI", "HMI_VALUEi": 0, "HMI_VALUEb": None, "PI_VALUEf": 0.12, "PI_VALUEb": None, "HMI_READi": 0})
    PIdb.insert({"INDEX": 51, "TAG":"RR1CDspeed_HMI", "HMI_VALUEi": 0, "HMI_VALUEb": None, "PI_VALUEf": 0.12, "PI_VALUEb": None, "HMI_READi": 0})
    PIdb.insert({"INDEX": 52, "TAG":"RR2ABspeed_HMI", "HMI_VALUEi": 0, "HMI_VALUEb": None, "PI_VALUEf": 0.12, "PI_VALUEb": None, "HMI_READi": 0})
    PIdb.insert({"INDEX": 53, "TAG":"Switch1Main_HMIb", "HMI_VALUEi": 0, "HMI_VALUEb": None, "PI_VALUEf": 0.12, "PI_VALUEb": False, "HMI_READi": 0})
    PIdb.insert({"INDEX": 54, "TAG":"open", "HMI_VALUEi": 0, "HMI_VALUEb": None, "PI_VALUEf": 0.12, "PI_VALUEb": False, "HMI_READi": 0})
    PIdb.insert({"INDEX": 55, "TAG":"Switch2RR3Main_HMIb", "HMI_VALUEi": 0, "HMI_VALUEb": None, "PI_VALUEf": 0.12, "PI_VALUEb": False, "HMI_READi": 0})
    PIdb.insert({"INDEX": 56, "TAG":"open", "HMI_VALUEi": 0, "HMI_VALUEb": None, "PI_VALUEf": 0.12, "PI_VALUEb": False, "HMI_READi": 0})
    PIdb.insert({"INDEX": 57, "TAG":"Switch3RR4Main_HMIb", "HMI_VALUEiy": 0, "HMI_VALUEb": None, "PI_VALUEf": 0.12, "PI_VALUEb": True, "HMI_READi": 0})
    PIdb.insert({"INDEX": 58, "TAG":"open", "HMI_VALUEi": 0, "HMI_VALUEb": None, "PI_VALUEf": 0.12, "PI_VALUEb": False, "HMI_READi": 0})
    PIdb.insert({"INDEX": 59, "TAG":"Switch4RR3Main_HMIb", "HMI_VALUEi": 0, "HMI_VALUEb": None, "PI_VALUEf": 0.12, "PI_VALUEb": False, "HMI_READi": 0})
    PIdb.insert({"INDEX": 60, "TAG":"open", "HMI_VALUEi": 0, "HMI_VALUEb": None, "PI_VALUEf": 0.12, "PI_VALUEb": False, "HMI_READi": 0})
    PIdb.insert({"INDEX": 61, "TAG":"Switch5Main_HMIb", "HMI_VALUEi": 0, "HMI_VALUEb": None, "PI_VALUEf": 0.12, "PI_VALUEb": False, "HMI_READi": 0 })
    PIdb.insert({"INDEX": 62, "TAG":"open", "HMI_VALUEi": 0, "HMI_VALUEb": None, "PI_VALUEf": 0.12, "PI_VALUEb": True, "HMI_READi": 0})
    PIdb.insert({"INDEX": 63, "TAG":"Switch6Main_HMIb", "HMI_VALUEi": 0, "HMI_VALUEb": None, "PI_VALUEf": 0.12, "PI_VALUEb": False, "HMI_READi": 0})
    PIdb.insert({"INDEX": 64, "TAG":"RR2orRR3Pwr_HMIb", "HMI_VALUEi": 0, "HMI_VALUEb": None, "PI_VALUEf": 0.12, "PI_VALUEb": False, "HMI_READi": 0})
    PIdb.insert({"INDEX": 65, "TAG":"TramStn1_HMIb", "HMI_VALUEi": 0, "HMI_VALUEb": None, "PI_VALUEf": 0.12, "PI_VALUEb": False, "HMI_READi": 0})
    PIdb.insert({"INDEX": 66, "TAG":"TramStn2_HMIb", "HMI_VALUEi": 0, "HMI_VALUEb": None, "PI_VALUEf": 0.12, "PI_VALUEb": False, "HMI_READi": 0})
    PIdb.insert({"INDEX": 67, "TAG":"TramStn3_HMIb", "HMI_VALUEi": 0, "HMI_VALUEb": None, "PI_VALUEf": 0.12, "PI_VALUEb": False, "HMI_READi": 0})
    PIdb.insert({"INDEX": 68, "TAG":"TramStn4_HMIb", "HMI_VALUEi": 0, "HMI_VALUEb": None, "PI_VALUEf": 0.12, "PI_VALUEb": True, "HMI_READi": 0})
    PIdb.insert({"INDEX": 69, "TAG":"TramStn5_HMIb", "HMI_VALUEi": 0, "HMI_VALUEb": None, "PI_VALUEf": 0.12, "PI_VALUEb": False, "HMI_READi": 0})
    PIdb.insert({"INDEX": 70, "TAG":"TramStn6_HMIb", "HMI_VALUEi": 0, "HMI_VALUEb": None, "PI_VALUEf": 0.12, "PI_VALUEb": False, "HMI_READi": 0})
    PIdb.insert({"INDEX": 71, "TAG":"PI_Future_1", "HMI_VALUEi": 0, "HMI_VALUEb": None, "PI_VALUEf": 0.12, "PI_VALUEb": False, "HMI_READi": 0})
    PIdb.insert({"INDEX": 72, "TAG":"PI_Future_2", "HMI_VALUEi": 0, "HMI_VALUEb": None, "PI_VALUEf": 0.12, "PI_VALUEb": False, "HMI_READi": 0})
    PIdb.insert({"INDEX": 73, "TAG":"PI_Future_3", "HMI_VALUEi": 0, "HMI_VALUEb": None, "PI_VALUEf": 0.12, "PI_VALUEb": False, "HMI_READi": 0})
    PIdb.insert({"INDEX": 74, "TAG":"PI_Future_4", "HMI_VALUEi": 0, "HMI_VALUEb": None, "PI_VALUEf": 0.12, "PI_VALUEb": False, "HMI_READi": 0})
    PIdb.insert({"INDEX": 75, "TAG":"PI_Future_5", "HMI_VALUEi": 0, "HMI_VALUEb": None, "PI_VALUEf": 0.12, "PI_VALUEb": False, "HMI_READi": 0})
    PIdb.insert({"INDEX": 76, "TAG":"PI_Future_6", "HMI_VALUEi": 0, "HMI_VALUEb": None, "PI_VALUEf": 0.12, "PI_VALUEb": False, "HMI_READi": 0})
    PIdb.insert({"INDEX": 77, "TAG":"PI_Future_6", "HMI_VALUEi": 0, "HMI_VALUEb": None, "PI_VALUEf": 0.12, "PI_VALUEb": False, "HMI_READi": 0})
    PIdb.insert({"INDEX": 78, "TAG":"PI_Future_8", "HMI_VALUEi": 0, "HMI_VALUEb": None, "PI_VALUEf": 0.12, "PI_VALUEb": False, "HMI_READi": 0})
    PIdb.insert({"INDEX": 79, "TAG":"PI_Future_9", "HMI_VALUEi": 0, "HMI_VALUEb": None, "PI_VALUEf": 0.12, "PI_VALUEb": False, "HMI_READi": 0})
    PIdb.insert({"INDEX": 80, "TAG":"PI_Future_10", "HMI_VALUEi": 0, "HMI_VALUEb": None, "PI_VALUEf": 0.12, "PI_VALUEb": False, "HMI_READi": 0})

def receive():
    global ServersendingUpdatesb, ServertoSendb, svrmsg
    while True:
        try:
            # Receive Message From Server   If 'NICK' Send Nickname
            svrmsg = client.recv(12288).decode(FORMAT)
            if svrmsg == 'NICK\n':
                client.send(NICKNAME.encode(FORMAT))
        except:
            # Close Connection When Error
            print("\nEXCEPT MSG: No Server Connection! check again in 1 second\n")
            # client.close()
            i = 0
            if i < 20:
                time.sleep(1.000)
                i += 1
                try:
                    svrmsg = client.recv(12288).decode(FORMAT)
                    if svrmsg == 'NICK':
                        client.send(NICKNAME.encode(FORMAT))
                except:
                    pass
            break	# stop running receive

        if svrmsg != "": # dont process blank lines while waiting
            print("\nFROM SERVER: \n", svrmsg)
            # For Updates from Server (Not Entire PIdb)
            if ServersendingUpdatesb and ServertoSendb:
                ServersendingUpdatesb, ServertoSendb = False, False
        time.sleep(0.050)

def handlePI():  			# Sending Messages To Server
    global ServersendingUpdatesb, PIdb, svrmsg
    SendUpdateDBb = False
    SendEntireDBb = False
    while True:
        time.sleep(0.067)
        x = ""
        print("New data?, PISendingUpdate, PIReadytoRecv, ServerSendEntiretoPI, ServerSendUpdatestoP, Zero")
        x = input("1=PINew?, 2=Send, 3=PIReadytoRecv, 4=Entire, 5=Updates, 6=Zero, 7=Print ")
        match int(x):
            case 1: #Is there new data?
                message = "PINew"
                try: client.send(message.encode(FORMAT))
                except: print("BROKEN PIPE to Server #176")

            case 2: # SEND PI UPDATES TO SERVER
                LocalUpdate()# update selected variable
                message = "PISendingUpdate"
                try: client.send(message.encode(FORMAT))
                except: print("BROKEN PIPE to Server #182")
                PItoServerUpdateSend = []
                PItoServerUpdate = []
                time.sleep(0.050)
                # pull PIdb rows values
                HMI_Readi = Xsend
                PItoServerUpdateSend = GetValuesforServer(PItoServerUpdate, HMI_Readi)
                #print("PItoServerUpdateSend:\n ", PItoServerUpdateSend)
                PItoServerUpdateSend = bytes(PItoServerUpdateSend, FORMAT)
                try: client.send(PItoServerUpdateSend.encode(FORMAT))
                except: print("BROKEN PIPE to Server #191")
                time.sleep(0.050)

            case 3: #PI ready for receive
                message = "PIReadytoRecv"
                try: client.send(message.encode(FORMAT))
                except: print("BROKEN PIPE to Server #197")
                time.sleep(0.050)
                if SendEntireDBb:
                    PIdb.purge() # Replace PI's Tinydb with server's
                    SendEntireDBb = False
                    json_data = json.loads(svrmsg)  # parse its JSON
                    for entry in json_data:  # iterate over each entry
                        PIdb.insert(entry)   # insert it in the DB
                if SendUpdateDBb:
                    while svrmsg == "Connected to server!": # wait
                        print("Waiting on server update")
                        time.sleep(0.050)
                        if svrmsg != "No Update Available":
                            PIdbUpdate(svrmsg)
                            SendUpdateDBb = False
                        else: print(svrmsg)

            case 4:  #PI requests the entire DB
                SendEntireDBb = True
                SendUpdateDBb = False
                message = "ServerSendEntiretoPI"
                try: client.send(message.encode(FORMAT))
                except: print("BROKEN PIPE to Server #218")
                print("Select 3 to execute command")

            case 5: #PI requests only updates in PIdb
                message = "ServerSendUpdatestoPI"
                try: client.send(message.encode(FORMAT))
                except: print("BROKEN PIPE to Server #224")
                SendEntireDBb = False
                SendUpdateDBb = True
                print("Select 3 to execute command")

            case 6: #Zero PI DB
                PIdb.update({"HMI_READi": 0})   # sets all vaues to 0 i column "HMI_READi"
                print(len(PIdb))
                #PIdb.truncate()
            case 7: #print PIDB
                print("\nPRINT PIdb\n ")
                for row in PIdb:
                    print(row)
                print(len(PIdb))
            case _: print("Select 1 through 7 only!") # out of range
    pass

# ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
# Place updated data in the PI Dictionary
def PIdbUpdate(ServerMessage):
    global PIdb
    try: json_data = json.loads(ServerMessage)
    except:
        print("Error")
        return
    print("length json_data[0]: ", len(json_data[0]))
    print(type(json_data[0][0]))
    for i in range(len(json_data[0])+1):
        Index = json_data[0][i].get("INDEX")
        HMI_Valuei = json_data[0][i].get("HMI_VALUEi")
        HMI_Valueb = json_data[0][i].get("HMI_VALUEb")
        PI_Valuef = json_data[0][i].get("PI_VALUEf")
        PI_Valueb = json_data[0][i].get("PI_VALUEb")
        HMI_Readi = json_data[0][i].get("HMI_READi")
        PIdb.update({"HMI_VALUEi": HMI_Valuei}, query.INDEX == Index)
        PIdb.update({"HMI_VALUEb": HMI_Valueb}, query.INDEX == Index)
        PIdb.update({"PI_VALUEf": PI_Valuef}, query.INDEX == Index)
        PIdb.update({"PI_VALUEb": PI_Valueb}, query.INDEX == Index)
        PIdb.update({"HMI_READi": HMI_Readi}, query.INDEX == Index)
    print("\nUPDATE COMPLETE\n Present PIdb is:\n")
    for row in PIdb:
        print(row)
#&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&
#Get values for Server to put in PIdb
# Index = 1 set by PI for HMI, 2 set by HMI for PI
def GetValuesforServer(PItoServerUpdate, HMI_Readi):
    global PIdb
    # server is ready to receive (calling code)
    print("In GetValuesforServer")
    PItoServerUpdate = ""
    temp = []
    temp.clear
    print("temp before: ", temp)
    print("HMI_Readi", HMI_Readi)
    #temp = PIdb.search(query["HMI_READi"] == HMI_Readi)
    temp = PIdb.search(query["HMI_READi"] == HMI_Readi)
    #    temp.append(PIdb.search(query["HMI_READi"] == HMI_Readi))
    PItoServerUpdate = json.dumps(temp) # LIST
    print(len(temp))
    print(type(temp))
    x=input("any key to print")
    print("temp", temp)
    return PItoServerUpdate

#^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#^^^^^^^^^^^^^ Local DB update for send to Server
def LocalUpdate(): # Update for PI or HMI
    yb = True   # stay in loop until update selected
    while yb:
        print("\nPI so update only for HMI, 50 to 80")
        print("\n 1='50 to 59' or 2='60 to 69' 3=you select")
        x = input("1, 2 or 3: ")
        match int(x):
            case 1:
                for i in range(50, 60):
                    print(i)
                    PIdb.update({"HMI_READi": 1}, query.INDEX == i)
                    print(PIdb.search(query.INDEX == i))
                yb = False
            case 2:
                for i in range(60, 70):
                    PIdb.update({"HMI_READi": 1}, query.INDEX == i)
                yb = False
            case 3:
                lower = int(input("Lower range: "))
                upper = int(input("Upper range: "))
                if lower < 50: lower = 50
                if upper > 80: upper = 80
                if lower > upper:
                    junk = lower
                    upper = lower
                    lower = junk
                for i in range(lower, upper):
                    PIdb.smartcache.update({"HMI_READi": 1}, query.INDEX == i)
                    #PIdb.smartcache.
                yb = False
            case _:
                print("SELECT 1, 2 or 3!")
# ***********************************************
# **************** MAIN **********************
PIdb.truncate()
PIdb.all()
LoadDB() # always load tinydb
# Starting Threads For Listening & handlePI
receive_thread = threading.Thread(target=receive,)
receive_thread.start()
print("Receive started")

handlePI_thread = threading.Thread(target=handlePI, )
handlePI_thread.start()
print("handlePI started")
