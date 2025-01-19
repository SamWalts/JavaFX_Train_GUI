from tkinter import ttk
import tkinter as tk
import functools
from time import strftime
import time
from time import sleep
from tinydb import TinyDB, Query
from tinydb.middlewares import CachingMiddleware
from tinydb.storages import JSONStorage
from tinydb.storages import MemoryStorage
import threading
import socket
import json
from json import dumps as json_dumps, loads as json_loads
from socket import error as SocketError

FORMAT = "utf-8"
# Nickname
NICKNAME = "paul" # UPDATE FOR CLIENT
query=Query()
fp = functools.partial
firstpass = True
BDfirstpassb = False
HMI_Valuei = 0  # Hold HMI value
HMI_Valueb = False  # Hold HMI value
message = "pass"    # holds message to send to server
terminal="pass"     # GUI terminal on display
class VerticalScrolledFrame(ttk.Frame):
    global svrmsg, UpdateServerf 
clientmsg = "pass"
UpdateServerf = 5.250
def Connection(Connectionb):
    for i in range(20):
        if not Connectionb:
            time.sleep(1.000)
            try: 
                client.connect(('127.0.0.1', 55555))
                Connectionb = True
            except ConnectionResetError: 
                terminal ="START SERVER!, CHECK every 1 sec for ", 20-i, " sec"
                print(terminal)
                time.sleep(1.000)
                Connectionb = False
            except ConnectionRefusedError: 
                print("Connection Refused Error")
                terminal = "Connection Refused Error"
        else: return Connectionb

    # Connecting To the Server
Connectionb = False
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
if not Connectionb:
    Connectionb = Connection(Connectionb) #client.connect(('127.0.0.1', 55555))
    svrmsg = "pass"
def handlepaul():
    global svrmsg, terminal
    print("GUI handlepaul started")
    while True:
        sleep(0.103) # free cpu time
        #print("paul svrmsg at top: ", svrmsg)
        if svrmsg =="pass" or svrmsg == "paulNo":
            message = "paulNew"
            client.send(message.encode(FORMAT))
        #print("sent paulNew")
        #while svrmsg == "PIYes" or svrmsg == "PINo":
        #    sleep(0.050)
        if svrmsg == "paulYes": # Server has PI update 
            message = "ReadytoRecv"
            client.send(message.encode(FORMAT))
            time.sleep(0.050)
            client.send("pass".encode(FORMAT))
        elif svrmsg.find("INDEX") >= 0: # not found = -1
    # Got data, save to local db - clear bit by program, not here
            json_data = json.loads(svrmsg)
            for row in range(0,len(json_data)):
                Index = json_data[row].get("INDEX")
                HMI_Valuei = json_data[row].get("HMI_VALUEi")
                HMI_Valueb = json_data[row].get("HMI_VALUEb")
                PI_Valuef = json_data[row].get("PI_VALUEf")
                PI_Valueb = json_data[row].get("PI_VALUEb")
                #HMI_Readi = json_data[row].get("HMI_READi")
                # ** PAUL SPECIAL, SET HMI_READi TO 0 **
                # ** Paul other registers for display **
                GUIdb.update({"HMI_VALUEi":HMI_Valuei,"HMI_VALUEb":HMI_Valueb,"PI_VALUEf":PI_Valuef,"PI_VALUEb":PI_Valueb,"HMI_READi":0},query.INDEX==Index)
                print("saved data: ", svrmsg)
        elif svrmsg == "ServerSENDDone": pass
            #print("Got ServerSENDDone")

     # Done with recieve, start the send 
        elif svrmsg == "paulNo": 
            if GUIdb.count(query.HMI_READi > 0) > 0:
                message = "SendingUpdates"
                client.send(message.encode(FORMAT))
                sleep(0.100)
            else: # nothing to send
                message = "\n NoUpdates"
                client.send(message.encode(FORMAT))
                sleep(0.100)
                message = "pass"
                client.send(message.encode(FORMAT))
        elif svrmsg == "ServerReady":
            print("in server ready section")
            ToZeroHMI_READi = GUIdb.search(query.HMI_READi > 0)
            message = json.dumps(ToZeroHMI_READi)
            client.send(message.encode(FORMAT)) # send updates
            print("GUI sent to Server: ", message)
            sleep(0.700)
            client.send("ClientSENDDone".encode(FORMAT))
            for row  in ToZeroHMI_READi: # ** SET HMI_READi TO 0 **
                ToZeroHMI_READiIndex = row.get("INDEX")
                GUIdb.update({"HMI_READi": 0}, query.INDEX == ToZeroHMI_READiIndex)

#&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&
def receive():
    global terminal, svrmsg
    print("receive started")
    terminal="receive started"
    while True:
        time.sleep(0.050) # give time to other threads
        svrmsg = client.recv(12288).decode(FORMAT) 
        if svrmsg == 'NICK':
            client.send(NICKNAME.encode(FORMAT))
            print('sent nickname ', NICKNAME)

def LoadGUIDB():
    GUIdb.insert({"INDEX": 1, "TAG":"HMI_RHT", "HMI_VALUEi": 25, "HMI_VALUEb": False, "PI_VALUEf": 0.0, "PI_VALUEb": True, "HMI_READi": 0})
    GUIdb.insert({"INDEX": 2, "TAG":"HMI_TramStopTime", "HMI_VALUEi": 9,"HMI_VALUEb":True, "PI_VALUEf": 0.0, "PI_VALUEb": True, "HMI_READi": 0})
    GUIdb.insert({"INDEX": 3, "TAG":"HMI_AllQuietb", "HMI_VALUEi": 0, "HMI_VALUEb": False, "PI_VALUEf": 0.0, "PI_VALUEb": True, "HMI_READi": 0})
    GUIdb.insert({"INDEX": 4, "TAG":"HMI_LIGHTONOFFb", "HMI_VALUEi": 0, "HMI_VALUEb": True, "PI_VALUEf": 0.0, "PI_VALUEb": True, "HMI_READi": 0})
    GUIdb.insert({"INDEX": 5, "TAG":"HMI_RR2_RR3Pwrb", "HMI_VALUEi": 0, "HMI_VALUEb": False, "PI_VALUEf": 0.0, "PI_VALUEb": True, "HMI_READi": 0})
    GUIdb.insert({"INDEX": 6, "TAG":"HMI_RRBellb", "HMI_VALUEi": 0, "HMI_VALUEb": True, "PI_VALUEf": 0.0, "PI_VALUEb": True, "HMI_READi": 0})
    GUIdb.insert({"INDEX": 7, "TAG":"HMI_RRDieselSteamb", "HMI_VALUEi": 0, "HMI_VALUEb": False, "PI_VALUEf": 0.0, "PI_VALUEb": True, "HMI_READi": 0})
    GUIdb.insert({"INDEX": 8, "TAG":"HMI_RRHornb", "HMI_VALUEi": 0, "HMI_VALUEb": True, "PI_VALUEf": 0.0, "PI_VALUEb": True, "HMI_READi": 0})
    GUIdb.insert({"INDEX": 9, "TAG":"HMI_RRQuietb", "HMI_VALUEi": 0, "HMI_VALUEb": False, "PI_VALUEf": 0.0, "PI_VALUEb": True, "HMI_READi": 0})
    GUIdb.insert({"INDEX": 10, "TAG":"HMI_RRWhistleb", "HMI_VALUEi": 0, "HMI_VALUEb": True, "PI_VALUEf": 0.0, "PI_VALUEb": True, "HMI_READi": 0})
    GUIdb.insert({"INDEX": 11, "TAG":"HMI_Switch1ABb", "HMI_VALUEi": 0, "HMI_VALUEb": True, "PI_VALUEf": 0.0, "PI_VALUEb": True, "HMI_READi": 0})
    GUIdb.insert({"INDEX": 12, "TAG":"HMI_Switch2RR3b", "HMI_VALUEi": 0, "HMI_VALUEb":True, "PI_VALUEf": 0.0, "PI_VALUEb": True, "HMI_READi": 0})
    GUIdb.insert({"INDEX": 13, "TAG":"HMI_Switch3RR4b", "HMI_VALUEi": 0, "HMI_VALUEb": True, "PI_VALUEf": 0.0, "PI_VALUEb":True, "HMI_READi": 0})
    GUIdb.insert({"INDEX": 14, "TAG":"HMI_Switch4RR3b", "HMI_VALUEi": 0, "HMI_VALUEb": True, "PI_VALUEf": 0.0, "PI_VALUEb": True, "HMI_READi": 0})
    GUIdb.insert({"INDEX": 15, "TAG":"HMI_Switch5ABb", "HMI_VALUEi": 0, "HMI_VALUEb": True, "PI_VALUEf": 0.0, "PI_VALUEb": True, "HMI_READi": 0})
    GUIdb.insert({"INDEX": 16, "TAG":"HMI_Switch6ABb", "HMI_VALUEi": 0, "HMI_VALUEb": True, "PI_VALUEf": 0.0, "PI_VALUEb": True, "HMI_READi": 0})
    GUIdb.insert({"INDEX": 17, "TAG":"HMI_TramQuietb", "HMI_VALUEi": 0, "HMI_VALUEb": True, "PI_VALUEf": 0.0, "PI_VALUEb": True, "HMI_READi": 0})
    GUIdb.insert({"INDEX": 18, "TAG":"HMI_TramStpStn_2b", "HMI_VALUEi":0, "HMI_VALUEb": True, "PI_VALUEf": 0.0, "PI_VALUEb":True, "HMI_READi": 0})
    GUIdb.insert({"INDEX": 19, "TAG":"HMI_TramStpStn_3b", "HMI_VALUEi": 0, "HMI_VALUEb": False, "PI_VALUEf": 0.0, "PI_VALUEb": True, "HMI_READi": 0})
    GUIdb.insert({"INDEX": 20, "TAG":"HMI_TramStpStn_5b", "HMI_VALUEi":0, "HMI_VALUEb": True, "PI_VALUEf": 0.0, "PI_VALUEb":True, "HMI_READi": 0})
    GUIdb.insert({"INDEX": 21, "TAG":"HMI_TramStpStn_6b", "HMI_VALUEi": 0, "HMI_VALUEb": False, "PI_VALUEf": 0.0, "PI_VALUEb": True, "HMI_READi": 0})
    GUIdb.insert({"INDEX": 22, "TAG":"HMI_Future_1", "HMI_VALUEi": 0, "HMI_VALUEb": True, "PI_VALUEf": 0.0, "PI_VALUEb": True, "HMI_READi": 0})
    GUIdb.insert({"INDEX": 23, "TAG":"HMI_Future_2", "HMI_VALUEi": 0, "HMI_VALUEb": True, "PI_VALUEf": 0.0, "PI_VALUEb": True, "HMI_READi": 0})
    GUIdb.insert({"INDEX": 24, "TAG":"HMI_Future_3", "HMI_VALUEi": 0, "HMI_VALUEb": True, "PI_VALUEf": 0.0, "PI_VALUEb": True, "HMI_READi": 0})
    GUIdb.insert({"INDEX": 25, "TAG":"HMI_Future_4", "HMI_VALUEi": 0, "HMI_VALUEb": True, "PI_VALUEf": 0.0, "PI_VALUEb": True, "HMI_READi": 0})
    GUIdb.insert({"INDEX": 26, "TAG":"HMI_Future_5", "HMI_VALUEi": 0, "HMI_VALUEb": True, "PI_VALUEf": 0.0, "PI_VALUEb": True, "HMI_READi": 0})
    GUIdb.insert({"INDEX": 27, "TAG":"HMI_Future_6", "HMI_VALUEi": 0, "HMI_VALUEb": True, "PI_VALUEf": 0.0, "PI_VALUEb": True, "HMI_READi": 0})
    GUIdb.insert({"INDEX": 28, "TAG":"HMI_Future_7", "HMI_VALUEi": 0, "HMI_VALUEb": True, "PI_VALUEf": 0.0, "PI_VALUEb": True, "HMI_READi": 0})
    GUIdb.insert({"INDEX": 29, "TAG":"HMI_Future_8", "HMI_VALUEi": 0, "HMI_VALUEb": True, "PI_VALUEf": 0.0, "PI_VALUEb": True, "HMI_READi": 0})
    GUIdb.insert({"INDEX": 30, "TAG":"HMI_Future_9", "HMI_VALUEi": 0, "HMI_VALUEb": True, "PI_VALUEf": 0.0, "PI_VALUEb": True, "HMI_READi": 0})
    GUIdb.insert({"INDEX": 31, "TAG":"HMI_Future_10", "HMI_VALUEi": 0, "HMI_VALUEb": True, "PI_VALUEf": 0.0, "PI_VALUEb": True, "HMI_READi": 0})
    GUIdb.insert({"INDEX": 32, "TAG":"HMI_Future_11", "HMI_VALUEi": 0, "HMI_VALUEb": True, "PI_VALUEf": 0.0, "PI_VALUEb": True, "HMI_READi": 0})
    GUIdb.insert({"INDEX": 33, "TAG":"HMI_Future_12", "HMI_VALUEi": 0, "HMI_VALUEb": True, "PI_VALUEf": 0.0, "PI_VALUEb": True, "HMI_READi": 0})
    GUIdb.insert({"INDEX": 34, "TAG":"HMI_Future_13", "HMI_VALUEi": 0, "HMI_VALUEb": True, "PI_VALUEf": 0.0, "PI_VALUEb": True, "HMI_READi": 0})
    GUIdb.insert({"INDEX": 35, "TAG":"HMI_Future_14", "HMI_VALUEi": 0, "HMI_VALUEb": True, "PI_VALUEf": 0.0, "PI_VALUEb": True, "HMI_READi": 0})
    GUIdb.insert({"INDEX": 36, "TAG":"HMI_Future_15", "HMI_VALUEi": 0, "HMI_VALUEb": True, "PI_VALUEf": 0.0, "PI_VALUEb": True, "HMI_READi": 0})
    GUIdb.insert({"INDEX": 37, "TAG":"HMI_Future_16", "HMI_VALUEi": 0, "HMI_VALUEb": True, "PI_VALUEf": 0.0, "PI_VALUEb": True, "HMI_READi": 0})
    GUIdb.insert({"INDEX": 38, "TAG":"HMI_Future_17", "HMI_VALUEi": 0, "HMI_VALUEb": True, "PI_VALUEf": 0.0, "PI_VALUEb": True, "HMI_READi": 0})
    GUIdb.insert({"INDEX": 39, "TAG":"HMI_Future_18", "HMI_VALUEi": 0, "HMI_VALUEb": True, "PI_VALUEf": 0.0, "PI_VALUEb": True, "HMI_READi": 0})
    GUIdb.insert({"INDEX": 40, "TAG":"HMI_Future_19", "HMI_VALUEi": 0, "HMI_VALUEb": True, "PI_VALUEf": 0.0, "PI_VALUEb": True, "HMI_READi": 0})
    GUIdb.insert({"INDEX": 41, "TAG":"HMI_Future_20", "HMI_VALUEi": 0, "HMI_VALUEb": True, "PI_VALUEf": 0.0, "PI_VALUEb": True, "HMI_READi": 0})
    GUIdb.insert({"INDEX": 42, "TAG":"HMI_Future_21", "HMI_VALUEi": 0, "HMI_VALUEb": True, "PI_VALUEf": 0.0, "PI_VALUEb": True, "HMI_READi": 0})
    GUIdb.insert({"INDEX": 43, "TAG":"HMI_Future_22", "HMI_VALUEi": 0, "HMI_VALUEb": True, "PI_VALUEf": 0.0, "PI_VALUEb": True, "HMI_READi": 0})
    GUIdb.insert({"INDEX": 44, "TAG":"HMI_Future_23", "HMI_VALUEi": 0, "HMI_VALUEb": True, "PI_VALUEf": 0.0, "PI_VALUEb": True, "HMI_READi": 0})
    GUIdb.insert({"INDEX": 45, "TAG":"HMI_Future_24", "HMI_VALUEi": 0, "HMI_VALUEb": True, "PI_VALUEf": 0.0, "PI_VALUEb": True, "HMI_READi": 0})
    GUIdb.insert({"INDEX": 46, "TAG":"HMI_Future_25", "HMI_VALUEi": 0, "HMI_VALUEb": True, "PI_VALUEf": 0.0, "PI_VALUEb": True, "HMI_READi": 0})
    GUIdb.insert({"INDEX": 47, "TAG":"HMI_Future_26", "HMI_VALUEi": 0, "HMI_VALUEb": True, "PI_VALUEf": 0.0, "PI_VALUEb": True, "HMI_READi": 0})
    GUIdb.insert({"INDEX": 48, "TAG":"HMI_Future_27", "HMI_VALUEi": 0, "HMI_VALUEb": True, "PI_VALUEf": 0.0, "PI_VALUEb": True, "HMI_READi": 0})
    GUIdb.insert({"INDEX": 49, "TAG":"HMI_Future_28", "HMI_VALUEi": 0, "HMI_VALUEb": True, "PI_VALUEf": 0.0, "PI_VALUEb":True, "HMI_READi": 0})
    GUIdb.insert({"INDEX": 50, "TAG":"RR1ABspeed_HMI", "HMI_VALUEi": 0, "HMI_VALUEb": True, "PI_VALUEf": 9.12, "PI_VALUEb": True, "HMI_READi": 0})
    GUIdb.insert({"INDEX": 51, "TAG":"RR1CDspeed_HMI", "HMI_VALUEi": 0, "HMI_VALUEb": True, "PI_VALUEf": 0.12, "PI_VALUEb": True, "HMI_READi": 0})
    GUIdb.insert({"INDEX": 52, "TAG":"RR2ABspeed_HMI", "HMI_VALUEi": 0, "HMI_VALUEb": True, "PI_VALUEf": 0.12, "PI_VALUEb": True, "HMI_READi": 0})
    GUIdb.insert({"INDEX": 53, "TAG":"Switch1Main_HMIb", "HMI_VALUEi": 0, "HMI_VALUEb": True, "PI_VALUEf": 0.12, "PI_VALUEb": True, "HMI_READi": 0})
    GUIdb.insert({"INDEX": 54, "TAG":"open", "HMI_VALUEi": 0, "HMI_VALUEb": True, "PI_VALUEf": 0.12, "PI_VALUEb": False, "HMI_READi": 0})
    GUIdb.insert({"INDEX": 55, "TAG":"Switch2RR3Main_HMIb", "HMI_VALUEi": 0, "HMI_VALUEb": True, "PI_VALUEf": 0.12, "PI_VALUEb": True, "HMI_READi": 0})
    GUIdb.insert({"INDEX": 56, "TAG":"open", "HMI_VALUEi": 0, "HMI_VALUEb": True, "PI_VALUEf": 0.12, "PI_VALUEb": False, "HMI_READi": 0})
    GUIdb.insert({"INDEX": 57, "TAG":"Switch3RR4Main_HMIb", "HMI_VALUEiy": 0, "HMI_VALUEb": True, "PI_VALUEf": 0.12, "PI_VALUEb": True, "HMI_READi": 0})
    GUIdb.insert({"INDEX": 58, "TAG":"open", "HMI_VALUEi": 0, "HMI_VALUEb": True, "PI_VALUEf": 0.12, "PI_VALUEb": False, "HMI_READi": 0})
    GUIdb.insert({"INDEX": 59, "TAG":"Switch4RR3Main_HMIb", "HMI_VALUEi": 0, "HMI_VALUEb": True, "PI_VALUEf": 0.12, "PI_VALUEb": True, "HMI_READi": 0})
    GUIdb.insert({"INDEX": 60, "TAG":"open", "HMI_VALUEi": 0, "HMI_VALUEb": True, "PI_VALUEf": 0.12, "PI_VALUEb": False, "HMI_READi": 0})
    GUIdb.insert({"INDEX": 61, "TAG":"Switch5Main_HMIb", "HMI_VALUEi": 0, "HMI_VALUEb": True, "PI_VALUEf": 0.12, "PI_VALUEb": True, "HMI_READi": 0 })
    GUIdb.insert({"INDEX": 62, "TAG":"open", "HMI_VALUEi": 0, "HMI_VALUEb": True, "PI_VALUEf": 0.12, "PI_VALUEb": True, "HMI_READi": 0})
    GUIdb.insert({"INDEX": 63, "TAG":"Switch6Main_HMIb", "HMI_VALUEi": 0, "HMI_VALUEb": True, "PI_VALUEf": 0.12, "PI_VALUEb": True, "HMI_READi": 0})
    GUIdb.insert({"INDEX": 64, "TAG":"RR2orRR3Pwr_HMIb", "HMI_VALUEi": 0, "HMI_VALUEb": True, "PI_VALUEf": 0.12, "PI_VALUEb": True, "HMI_READi": 0})
    GUIdb.insert({"INDEX": 65, "TAG":"TramStn1_HMIb", "HMI_VALUEi": 0, "HMI_VALUEb": True, "PI_VALUEf": 0.12, "PI_VALUEb": False, "HMI_READi": 0})
    GUIdb.insert({"INDEX": 66, "TAG":"TramStn2_HMIb", "HMI_VALUEi": 0, "HMI_VALUEb": True, "PI_VALUEf": 0.12, "PI_VALUEb": False, "HMI_READi": 0})
    GUIdb.insert({"INDEX": 67, "TAG":"TramStn3_HMIb", "HMI_VALUEi": 0, "HMI_VALUEb": True, "PI_VALUEf": 0.12, "PI_VALUEb": False, "HMI_READi": 0})
    GUIdb.insert({"INDEX": 68, "TAG":"TramStn4_HMIb", "HMI_VALUEi": 0, "HMI_VALUEb": True, "PI_VALUEf": 0.12, "PI_VALUEb": True, "HMI_READi": 0})
    GUIdb.insert({"INDEX": 69, "TAG":"TramStn5_HMIb", "HMI_VALUEi": 0, "HMI_VALUEb": True, "PI_VALUEf": 0.12, "PI_VALUEb": False, "HMI_READi": 0})
    GUIdb.insert({"INDEX": 70, "TAG":"TramStn6_HMIb", "HMI_VALUEi": 0, "HMI_VALUEb": True, "PI_VALUEf": 0.12, "PI_VALUEb": False, "HMI_READi": 0})
    GUIdb.insert({"INDEX": 71, "TAG":"PI_Future_1", "HMI_VALUEi": 0, "HMI_VALUEb": True, "PI_VALUEf": 0.12, "PI_VALUEb": False, "HMI_READi": 0})
    GUIdb.insert({"INDEX": 72, "TAG":"PI_Future_2", "HMI_VALUEi": 0, "HMI_VALUEb": True, "PI_VALUEf": 0.12, "PI_VALUEb": False, "HMI_READi": 0})
    GUIdb.insert({"INDEX": 73, "TAG":"PI_Future_3", "HMI_VALUEi": 0, "HMI_VALUEb": True, "PI_VALUEf": 0.12, "PI_VALUEb": False, "HMI_READi": 0})
    GUIdb.insert({"INDEX": 74, "TAG":"PI_Future_4", "HMI_VALUEi": 0, "HMI_VALUEb": True, "PI_VALUEf": 0.12, "PI_VALUEb": False, "HMI_READi": 0})
    GUIdb.insert({"INDEX": 75, "TAG":"PI_Future_5", "HMI_VALUEi": 0, "HMI_VALUEb": True, "PI_VALUEf": 0.12, "PI_VALUEb": False, "HMI_READi": 0})
    GUIdb.insert({"INDEX": 76, "TAG":"PI_Future_6", "HMI_VALUEi": 0, "HMI_VALUEb": True, "PI_VALUEf": 0.12, "PI_VALUEb": False, "HMI_READi": 0})
    GUIdb.insert({"INDEX": 77, "TAG":"PI_Future_6", "HMI_VALUEi": 0, "HMI_VALUEb": True, "PI_VALUEf": 0.12, "PI_VALUEb": False, "HMI_READi": 0})
    GUIdb.insert({"INDEX": 78, "TAG":"PI_Future_8", "HMI_VALUEi": 0, "HMI_VALUEb": True, "PI_VALUEf": 0.12, "PI_VALUEb": False, "HMI_READi": 0})
    GUIdb.insert({"INDEX": 79, "TAG":"PI_Future_9", "HMI_VALUEi": 0, "HMI_VALUEb": True, "PI_VALUEf": 0.12, "PI_VALUEb": False, "HMI_READi": 0})
    GUIdb.insert({"INDEX": 80, "TAG":"PI_Future_10", "HMI_VALUEi": 0, "HMI_VALUEb": True, "PI_VALUEf": 0.12, "PI_VALUEb": False, "HMI_READi": 0})
if not BDfirstpassb: 
    GUIdb = TinyDB(storage=MemoryStorage)
    BDfirstpassb = True
#GUIdb.truncate()    # clear db so fresh everytime
print("count = :",len(GUIdb))
if (len(GUIdb)) < 10:
    print("count: ", GUIdb.count(["INDEX"]==0))
    LoadGUIDB()
 
def __init__(self, parent, *args, **kw):

    # track changes to the canvas and frame width and sync them,
    # also updating the scrollbar
    def _configure_interior(event):
        # update the scrollbars to match the size of the inner frame
        size=(interior.winfo_reqwidth(),interior.winfo_reqheight())
        canvas.config(scrollregion="0 0 %s %s" % size)
        if interior.winfo_reqwidth() != canvas.winfo_width():
            # update the canvas's width to fit the inner frame
            canvas.config(width=interior.winfo_reqwidth())

    def _configure_canvas(event):
        if interior.winfo_reqwidth() != canvas.winfo_width():
            # update the inner frame's width to fill the canvas
            canvas.itemconfigure(interior_id, width=canvas.winfo_width())
    """
    This is linux code for scrolling the window, 
    It has different buttons for scrolling the windows
    """
    def _on_mousewheel(event, scroll):
        canvas.yview_scroll(int(scroll), "units")

    def _bind_to_mousewheel(event):
        canvas.bind_all("<Button-4>", fp(_on_mousewheel, scroll=-1))
        canvas.bind_all("<Button-5>", fp(_on_mousewheel, scroll=1))

    def _unbind_from_mousewheel(event):
        canvas.unbind_all("<Button-4>")
        canvas.unbind_all("<Button-5>")

    ttk.Frame.__init__(self, parent, *args, **kw)

        # create a canvas object and a vertical scrollbar for scrolling it
    vscrollbar = ttk.Scrollbar(self, orient=tk.VERTICAL)
    vscrollbar.pack(fill=tk.Y, side=tk.RIGHT, expand=tk.FALSE,padx=0,)
    
    canvas = tk.Canvas(self, bd=0, highlightthickness=1,
                        yscrollcommand=vscrollbar.set,height=40, width=10)
    canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=tk.TRUE)
    vscrollbar.config(command=canvas.yview)

    # reset the view
    canvas.xview_moveto(0)
    canvas.yview_moveto(0)

    # create a frame inside the canvas which will be scrolled with it
    self.interior = interior = ttk.Frame(canvas, height=1000, width=1000)
    interior_id = canvas.create_window(0,0,window=interior,anchor=tk.NW,height=1000, width=1300)
    interior.bind('<Configure>', _configure_interior)
    canvas.bind('<Configure>', _configure_canvas)
    canvas.bind('<Enter>', _bind_to_mousewheel)
    canvas.bind('<Leave>', _unbind_from_mousewheel)

if __name__ == "__main__":

    # Set Up root of app
    root = tk.Tk()
    root.geometry("1200x800+50+50")
    root.title("Pauvo, James, Kathern, William, Tinkerbell's TRAIN")

    # Create a frame to put the VerticalScrolledFrame inside
    holder_frame = tk.Frame(root)
    holder_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=tk.TRUE)
    holder_frame.size()
    # Create the VerticalScrolledFrame
    def HMI_Interface(a,index,zz):
        Failedb = False
        #zz=int(zz)
        try: index = int(index) # IntVar cant convert
        except TypeError: pass
        print("in HMI_Interface")
        if index<=3:   # HMI to P data
            GUIdb.update({"HMI_VALUEi":zz, "HMI_READi":2},query.INDEX == index)
            print (GUIdb.get(query['INDEX'] == index))
            time.sleep(1)
        if index >=3 and index < 50:  # Boolean-HMI to PI data
            temp = GUIdb.get(query['INDEX'] == index)
            temp1 = temp.get("HMI_VALUEb")
            temp1=not temp1
            GUIdb.update({"HMI_VALUEb":temp1, "HMI_READi":1}, query.INDEX == index)
        elif index>=50 and index<=52:
                try:
                    zz = float(zz)
                except ValueError:
                    zz = 0.0
                if zz>=0.0 and zz<= 99:
                    GUIdb.update({"PI_VALUEf":zz, "HMI_READi":2}, query.INDEX == index)
                    Failedb = False
                else:
                    Failedb = True
                    print("Failedb = ", Failedb)
                    print("conversion Failed")
                    zz = 0.0 
        elif index ==65: # station 1, at station
            temp = GUIdb.get(query['INDEX'] == index)
            temp1 = temp.get("PI_VALUEb")
            temp1=not temp1
            GUIdb.update({"PI_VALUEb":temp1, "HMI_READi":1}, query.INDEX == index)            
        elif index ==66: # station 2, at station
            temp = GUIdb.get(query['INDEX'] == index)
            temp1 = temp.get("PI_VALUEb")
            temp1=not temp1
            GUIdb.update({"PI_VALUEb":temp1, "HMI_READi":1}, query.INDEX == index)  
        elif index ==67: # station 3, at station
            temp = GUIdb.get(query['INDEX'] == index)
            temp1 = temp.get("PI_VALUEb")
            temp1=not temp1
            GUIdb.update({"PI_VALUEb":temp1, "HMI_READi":1}, query.INDEX == index)  
        elif index ==68: # station 4, at station
            temp = GUIdb.get(query['INDEX'] == index)
            temp1 = temp.get("PI_VALUEb")
            temp1=not temp1
            GUIdb.update({"PI_VALUEb":temp1, "HMI_READi":1}, query.INDEX == index) 
        elif index ==69: # station 5, at station
            temp = GUIdb.get(query['INDEX'] == index)
            temp1 = temp.get("PI_VALUEb")
            temp1=not temp1
            GUIdb.update({"PI_VALUEb":temp1, "HMI_READi":1}, query.INDEX == index)  
        elif index ==70: # station 6, at station
            temp = GUIdb.get(query['INDEX'] == index)
            temp1 = temp.get("PI_VALUEb")
            temp1=not temp1
            GUIdb.update({"PI_VALUEb":temp1, "HMI_READi":1}, query.INDEX == index)             
        return Failedb
    def Print(who):
        if who == "HMI":
            for i in range(1,50):  
                temp = GUIdb.get(query['INDEX'] == i)
                print(temp)
        elif who == "PI":
            for i in range(50,70):  
                temp = GUIdb.get(query['INDEX'] == i)
                print(temp)
        elif who == "ALL":
            for row in GUIdb:
                print(row)
        elif who == "Server":
            message = "Print Server"
            client.send(message.encode(FORMAT)) 
    def Time():
        global UpdateServerf
        time_string = strftime('%H:%M:%S')
        timelbl.configure(text=time_string)
        UpdateServerf= float(UpdateServerspin.get())
        Terminal.configure(text=terminal)
        timelbl.after(1000, Time)
    def UpdateSpeed1a():
        temp = GUIdb.get(query['INDEX'] == 50)
        temp1 = str(temp.get("PI_VALUEf"))
        HMI_lbl1d.configure(text=temp1)
        HMI_lbl1d.after(1050, UpdateSpeed1a)
    def UpdateSpeed1c():
        temp = GUIdb.get(query['INDEX'] == 51)
        temp1 = str(temp.get("PI_VALUEf"))
        HMI_lbl2d.configure(text=temp1)
        HMI_lbl2d.after(1055, UpdateSpeed1c) 
    def UpdateSpeed2a():
        temp = GUIdb.get(query['INDEX'] == 52)
        temp1 = str(temp.get("PI_VALUEf"))
        HMI_lbl3d.configure(text=temp1)
    def UpdateHMIRHT():
        temp = GUIdb.get(query['INDEX'] == 1)
        temp1 = temp.get("HMI_VALUEi")
        PI_lbl4h.configure(text=temp1)
        PI_lbl4h.after(1100, UpdateHMIRHT) 

    AutoFlipValueb = tk.BooleanVar() # used for showing whether switch feedback is enabled or not
    
    def UpdateHMI_TramStopTime():
        temp = GUIdb.get(query['INDEX'] == 2)
        temp1 = temp.get("HMI_VALUEi")
        PI_lbl5h.configure(text=temp1)
        PI_lbl5h.after(1200, UpdateHMI_TramStopTime) 

    def UpdatePISwitchControl(HMIIndex, PIIndex): # called by UpdatePISwitch1
        match HMIIndex:
            case 11: HMI_x= HMI_lbl14d # switch 1
            case 12: HMI_x= HMI_lbl15d # switch 2
            case 13: HMI_x= HMI_lbl16d # switch 3
            case 14: HMI_x= HMI_lbl17d # switch 4
            case 15: HMI_x= HMI_lbl18d # switch 5
            case 16: HMI_x= HMI_lbl19d # switch 6
        temp = GUIdb.get(query['INDEX'] == HMIIndex)    
        HMI_bValue = temp.get("HMI_VALUEb")
        if HMI_bValue: HMI_x.configure(text="RR1<>RR2", bg="lawngreen")
        else: HMI_x.configure(text="RR1=RR2", bg="salmon")
        match PIIndex:
            case 53: # switch 1
                PI_xg= PI_btn14g
                PI_xh= PI_lbl14h 
            case 55: # switch 2
                PI_xg= PI_btn15g
                PI_xh= PI_lbl15h  
            case 57: # switch 3
                PI_xg= PI_btn16g
                PI_xh= PI_btn16h 
            case 59: # switch 4
                PI_xg= PI_lbl17g
                PI_xh= PI_btn17h 
            case 61: # switch 5
                PI_xg= PI_lbl18g
                PI_xh= PI_btn18h 
            case 63: # switch 6
                PI_xg= PI_lbl19g
                PI_xh= PI_btn19h 
        temp = GUIdb.get(query['INDEX'] == PIIndex)    
        PI_bValue = temp.get("PI_VALUEb")
        if AutoFlipValueb.get(): # true, add time and match HMI cmd without PI
            PI_xg.configure(text="manual delay",bg="lightgrey")  
            PI_xh.configure(text="auto delay",bg="lightgrey")
            time.sleep(float(AutoFlipspin.get()))
            PI_bValue = HMI_bValue
        if PI_bValue: # True
            PI_xg.configure(text="RR1<>RR2", bg="lawngreen") 
            PI_xh.configure(text="not cnncted", bg="lawngreen") 
        else: #False
            PI_xg.configure(text="RR1=RR2", bg="salmon") 
            PI_xh.configure(text="connected", bg="salmon") 
    def UpdatePISwitch1(): # scanned every x seconds
        for i in range(18,22): #Tram 2, 3, 5, 6. 1 & 4 must stop
            Tramtemp = GUIdb.get(query['INDEX'] == i)
            Tramtemp1 = Tramtemp.get("HMI_VALUEb")
            if Tramtemp1: textHMI, back="Will Stop", "yellowgreen" 
            else: textHMI, back="Bypass", "goldenrod"
            match i: #feedback to HMI Tram Bypass selection
                case 18: HMI_btn22c.configure(text=textHMI, bg=back) 
                case 19: HMI_btn23c.configure(text=textHMI, bg=back)
                case 20: HMI_btn25c.configure(text=textHMI, bg=back)
                case 21: HMI_btn26c.configure(text=textHMI, bg=back)               
        for i in range(53,64):
            match i: #feedback to HMI switch selection
                case 53: #  Switch 1
                    HMIIndex = 11 #  PIIndex = i
                    UpdatePISwitchControl(HMIIndex, i) # HMIIndex, i = PIIndex
                case 55: #  Switch 2
                    HMIIndex = 12
                    UpdatePISwitchControl(HMIIndex, i) # HMIIndex, i = PIIndex
                case 57: #  Switch 3
                    HMIIndex = 13   
                    UpdatePISwitchControl(HMIIndex, i) # HMIIndex, i = PIIndex
                case 59: #  Switch 4
                    HMIIndex = 14
                    UpdatePISwitchControl(HMIIndex, i) # HMIIndex, i = PIIndex
                case 61: #  Switch 5
                    HMIIndex = 15
                    UpdatePISwitchControl(HMIIndex, i) # HMIIndex, i = PIIndex
                case 63: #  Switch 6
                    HMIIndex = 16
                    UpdatePISwitchControl(HMIIndex, i) # HMIIndex, i = PIIndex
        
        
        PI_lbl14h.after(500, UpdatePISwitch1)

    def UpdateSwitchFdBck(a,index,b): # sets feedback on switches for HMI display
            if AutoFlipValueb.get():time.sleep(float(AutoFlipspin.get()))
            match index: #feedback to HMI switch selection
                case 53: #  Switch 1 Feedback
                    temp = GUIdb.get(query['INDEX'] == 11)
                    temp1 = temp.get("HMI_VALUEb")
                    if not AutoFlipValueb.get():
                        GUIdb.update({"PI_VALUEb":temp1,"HMI_READi":0},query.INDEX==index)
                        time.sleep(0.025)
                        temp = GUIdb.get(query['INDEX'] == index)
                        temp1 = temp.get("PI_VALUEb")
                        if temp1: 
                            PI_btn14g.configure(text="RR1<>RR2",bg="lawngreen")
                            PI_lbl14h.configure(text="not cnncted",bg="lawngreen")
                        else: 
                            PI_btn14g.configure(text="RR1=RR2",bg="salmon")
                            PI_lbl14h.configure(text="connected",bg="salmon") 
                case 55: #  Switch 2 Feedback
                    temp = GUIdb.get(query['INDEX'] == 12)
                    temp1 = temp.get("HMI_VALUEb")
                    if not AutoFlipValueb.get():
                        GUIdb.update({"PI_VALUEb":temp1,"HMI_READi":1},query.INDEX==index)
                        time.sleep(0.025)
                        temp = GUIdb.get(query['INDEX'] == index)
                        temp1 = temp.get("PI_VALUEb")
                        if temp1: 
                            PI_btn15g.configure(text="RR2<>RR3",bg="lawngreen")
                            PI_lbl15h.configure(text="not cnncted",bg="lawngreen")
                        else: 
                            PI_btn15g.configure(text="RR2=RR3",bg="salmon")
                            PI_lbl15h.configure(text="connected",bg="salmon") 
                case 57: #  Switch 3 Feedback
                    temp = GUIdb.get(query['INDEX'] == 13)
                    temp1 = temp.get("HMI_VALUEb")
                    if not AutoFlipValueb.get():
                        GUIdb.update({"PI_VALUEb":temp1,"HMI_READi":1},query.INDEX==index)
                        time.sleep(0.025)
                        temp = GUIdb.get(query['INDEX'] == index)
                        temp1 = temp.get("PI_VALUEb")
                        if temp1: 
                            PI_btn16g.configure(text="RR3<>RR4",bg="lawngreen")
                            PI_btn16h.configure(text="not cnncted",bg="lawngreen")
                        else: 
                            PI_btn16g.configure(text="RR3=RR4",bg="salmon")
                            PI_btn16h.configure(text="connected",bg="salmon") 
                case 59: #  Switch 4 Feedback
                    temp = GUIdb.get(query['INDEX'] == 14)
                    temp1 = temp.get("HMI_VALUEb")
                    if not AutoFlipValueb.get():
                        GUIdb.update({"PI_VALUEb":temp1,"HMI_READi":1},query.INDEX==index)
                        time.sleep(0.025)
                        temp = GUIdb.get(query['INDEX'] == index)
                        temp1 = temp.get("PI_VALUEb")
                        if temp1: 
                            PI_lbl17g.configure(text="RR3<>RR4",bg="lawngreen")
                            PI_btn17h.configure(text="not cnncted",bg="lawngreen")
                        else: 
                            PI_lbl17g.configure(text="RR3=RR4",bg="salmon")
                            PI_btn17h.configure(text="connected",bg="salmon") 
                case 61: #  Switch 5 Feedback
                    temp = GUIdb.get(query['INDEX'] == 15)
                    temp1 = temp.get("HMI_VALUEb")
                    if not AutoFlipValueb.get():
                        GUIdb.update({"PI_VALUEb":temp1,"HMI_READi":1},query.INDEX==index)
                        time.sleep(0.025)
                        temp = GUIdb.get(query['INDEX'] == index)
                        temp1 = temp.get("PI_VALUEb")
                        if temp1: 
                            PI_lbl18g.configure(text="RR2<>RR3",bg="lawngreen")
                            PI_btn18h.configure(text="not cnncted",bg="lawngreen")
                        else: 
                            PI_lbl18g.configure(text="RR2=RR3",bg="salmon")
                            PI_btn18h.configure(text="connected",bg="salmon") 
                case 63: #  Switch 1 Feedback
                    temp = GUIdb.get(query['INDEX'] == 16)
                    temp1 = temp.get("HMI_VALUEb")
                    if not AutoFlipValueb.get():
                        GUIdb.update({"PI_VALUEb":temp1,"HMI_READi":1},query.INDEX==index)
                        time.sleep(0.025)
                        temp = GUIdb.get(query['INDEX'] == index)
                        temp1 = temp.get("PI_VALUEb")
                        if temp1: 
                            PI_lbl19g.configure(text="RR1<>RR2",bg="lawngreen")
                            PI_btn19h.configure(text="not cnncted",bg="lawngreen")
                        else: 
                            PI_lbl19g.configure(text="RR1=RR2",bg="salmon")
                            PI_btn19h.configure(text="connected",bg="salmon") 

    def HMI_PB(a,index,b):
        if index<22:
            temp = GUIdb.get(query['INDEX'] == index)
            temp1HMI = temp.get("HMI_VALUEb")
            temp1HMI = not temp1HMI
            GUIdb.update({"HMI_VALUEb":temp1HMI, "HMI_READi":2}, query.INDEX == index)
        elif index>70 and index<99:
            temp = GUIdb.get(query['INDEX'] == index)
            temp1HMI = temp.get("PI_VALUEb")
            temp1HMI = not temp1HMI
            GUIdb.update({"PI_VALUEb":temp1, "HMI_READi":1}, query.INDEX == index)
        match index:          
            case 3:
                if temp1HMI: HMI_lbl6d.configure(text="no snds",bg="lawngreen")
                else: HMI_lbl6d.configure(text="snds OK",bg="sandybrown")
                PI_lbl6h.configure(text=temp1HMI)
            case 4:
                if temp1HMI: HMI_lbl7d.configure(text="lghts ON", bg="lawngreen")
                else: HMI_lbl7d.configure(text="Lghts OFF",bg="sandybrown")
                PI_lbl7h.configure(text=str(temp1HMI))
            case 5:
                if temp1HMI: HMI_lbl8d.configure(text="RR2 PWR",bg="lawngreen")
                else: HMI_lbl8d.configure(text="RR3 PWR", bg="sandybrown")
                PI_lbl8h.configure(text=str(temp1HMI))
            case 6:
                if temp1HMI: HMI_lbl9d.configure(text="bell",bg="lawngreen")
                else: HMI_lbl9d.configure(text="-no bell-",bg="sandybrown")
                PI_lbl9h.configure(text=temp1HMI)
            case 7:
                HMI_lbl10d.configure(text=temp1HMI)
                PI_lbl10h.configure(text=temp1HMI)
            case 8:
                if temp1HMI: HMI_lbl11d.configure(text="HORN", bg="lawngreen")
                else: HMI_lbl11d.configure(text="-no horn-",bg="sandybrown")
                PI_lbl11h.configure(text=temp1HMI)
            case 9:
                if temp1HMI: HMI_lbl12d.configure(text="RR sound",bg="lawngreen")
                else: HMI_lbl12d.configure(text="no RR snd",bg="sandybrown")
                PI_lbl12h.configure(text=str(temp1HMI))
            case 10:
                if temp1HMI: HMI_lbl13d.configure(text="whistle", bg="lawngreen")
                else: HMI_lbl13d.configure(text="-no whistle-", bg="sandybrown")
                PI_lbl13h.configure(text=str(temp1HMI))
            case 11:    
                HMI_lbl14d.configure(text=str(temp1HMI))
            case 12:
                HMI_lbl15d.configure(text=str(temp1HMI))
            case 13:
                HMI_lbl16d.configure(text=str(temp1HMI))
            case 14:
                HMI_lbl17d.configure(text=str(temp1HMI))
            case 15:
                HMI_lbl18d.configure(text=str(temp1HMI))
            case 16:
                HMI_lbl19d.configure(text=str(temp1HMI))
            case 17:
                if temp1HMI: HMI_lbl20d.configure(text="Tram quiet",bg="lawngreen")
                else: HMI_lbl20d.configure(text="Tram Snd",bg="sandybrown")
                
            case 18:   # station 2 Stn 1 has no OPTION, must stop
                pass
                #if temp1HMI==True: textTram, back="stop(prs)", "lawngreen"
                #else: textTram, back="bypss(prs)", "sandybrown"
                #HMI_btn22c.configure(text=str(textTram), bg=back)
                #PI_lbl22h.configure(text=str(textTram), bg=back)
            case 19: # station 3
                if temp1HMI==True: textTram, back="stop", "lawngreen"
                else: textTram, back="bypass", "sandybrown"
                HMI_lbl23d.configure(text=str(textTram), bg=back)
                PI_lbl23h.configure(text=str(textTram), bg=back)
            case 20:   # station 5 stn 4 has no OPTION, must stop
                if temp1HMI==True: textTram, back="stop", "lawngreen"
                else: textTram, back="bypass", "sandybrown"
                HMI_lbl25d.configure(text=str(textTram), bg=back)
                PI_lbl25h.configure(text=str(textTram), bg=back)
            case 21: # station 6
                if temp1HMI==True: textTram, back="stop", "lawngreen"
                else: textTram, back="bypass", "sandybrown"
                HMI_lbl26d.configure(text=str(textTram), bg=back)
                PI_lbl26h.configure(text=str(textTram), bg=back)
            case 65: #  station 1, at station PI BIT USED
                if temp1: temp1PI,back="@ STN", "lawngreen"
                else: temp1PI, back="not @ STN","sandybrown"
                HMI_lbl21d.configure(text=temp1PI,bg=back)
                PI_lbl21h.configure(text=temp1PI,bg=back)
            case 66: #  station 2, at station
                if temp1: temp1PI,back="@ STN", "lawngreen"
                else: temp1PI, back="not @ STN","sandybrown"
                if HMI_lbl22d.cget("text") == "bypass": HMI_lbl22d.configure(text="NO STOP",bg="sandybrown")
                else: HMI_lbl22d.configure(text=temp1PI,bg=back)
                PI_lbl22h.configure(text=temp1PI,bg=back)
            case 67: #  station 3, at station
                if temp1: temp1PI,back="@ STN", "lawngreen"
                else: temp1PI, back="not @ STN","sandybrown"
                if HMI_lbl23d.cget("text") == "bypass": HMI_lbl23d.configure(text="NO STOP",bg="sandybrown")
                else: HMI_lbl23d.configure(text="bypass",bg=back)
                PI_lbl23h.configure(text=temp1,bg=back)
            case 68: #  station 4, at station
                if temp1: temp1,back="@ STN", "lawngreen"
                else: temp1, back="not @ STN","sandybrown"
                HMI_lbl24d.configure(text=temp1,bg=back)
                PI_lbl24h.configure(text=temp1,bg=back)
            case 69: #  station 5, at station
                if temp1: temp1,back="@ STN", "lawngreen"
                else: temp1, back="not @ STN","sandybrown"
                if HMI_lbl25d.cget("text") == "bypass": HMI_lbl25d.configure(text="NO STOP",bg="sandybrown")
                else: HMI_lbl25d.configure(text="bypass",bg=back)
                PI_lbl25h.configure(text=temp1,bg=back)
            case 70: #  station 6, at station
                if temp1: temp1,back="@ STN", "lawngreen"
                else: temp1, back="not @ STN","salmon"
                if HMI_lbl26d.cget("text") == "bypass": HMI_lbl26d.configure(text="NO STOP",bg="sandybrown")
                else: HMI_lbl26d.configure(text="bypass",bg="sandybrown")
                PI_lbl26h.configure(text=temp1,bg=back)

    def Switches(a,index,Fromi): #Manage switches & feedback
        if Fromi==2:    #From HMI to PI, PI to give feedback
            temp = GUIdb.get(query['INDEX'] == index)
            temp1 = temp.get("HMI_VALUEb")
            temp1 = not temp1
            GUIdb.update({"HMI_VALUEb":temp1, "HMI_READi":2}, query.INDEX == index)

    vs_frame = VerticalScrolledFrame(holder_frame)
    vs_frame.pack_propagate(1)
    vs_frame.grid(row=0, column=0, rowspan=100,columnspan=11)
    
    # load HMI Index
    HMIIndex01 = tk.IntVar(vs_frame, value = 1) # Relay Hold Time
    HMIIndex02 = tk.IntVar(vs_frame, value = 2) # HMI_TramStopTime
    HMIIndex03 = tk.IntVar(vs_frame, value = 3) # HMI_AllQuietb
    HMIIndex04 = tk.IntVar(vs_frame, value = 4) # HMI_LIGHTONOFFb
    HMIIndex05 = tk.IntVar(vs_frame, value = 5) # HMI_RR2_RR3Pwrb
    HMIIndex06 = tk.IntVar(vs_frame, value = 6) # HMI_RRBellb
    HMIIndex07 = tk.IntVar(vs_frame, value = 7) # HMI_RRDieselSteamb
    HMIIndex08 = tk.IntVar(vs_frame, value = 8) # HMI_RRHornb
    HMIIndex09 = tk.IntVar(vs_frame, value = 9) # HMI_RRQuiteb
    HMIIndex10 = tk.IntVar(vs_frame, value = 10) # HMI_RRWhistleb
    HMIIndex11 = tk.IntVar(vs_frame, value = 11) # HMI_Switch1ABb
    HMIIndex12 = tk.IntVar(vs_frame, value = 12) # HMI_Switch2RR3b
    HMIIndex13 = tk.IntVar(vs_frame, value = 13) # HMI_Switch3RR4b
    HMIIndex14 = tk.IntVar(vs_frame, value = 14) # HMI_Switch4RR3b
    HMIIndex15 = tk.IntVar(vs_frame, value = 15) # HMI_Switch5RR4b
    HMIIndex16 = tk.IntVar(vs_frame, value = 16) # HMI_Switch6RR5b
    HMIIndex17 = tk.IntVar(vs_frame, value = 17) # HMI_TramQuietb
    HMIIndex18 = tk.IntVar(vs_frame, value = 18) # HMI_TramStpStn_2b
    HMIIndex19 = tk.IntVar(vs_frame, value = 19) # HMI_TramStpStn_3b
    HMIIndex20 = tk.IntVar(vs_frame, value = 20) # HMI_TramStpStn_5b
    HMIIndex21 = tk.IntVar(vs_frame, value = 21) # HMI_TramStpStn_6b
    # Load  PIIndex constants, used by other threads 
    # -Replace with constants?
    PIIndex50 = tk.IntVar(vs_frame, value = 50) # speed 1AB
    PIIndex51 = tk.IntVar(vs_frame, value = 51) # speed 1CD
    PIIndex52 = tk.IntVar(vs_frame, value = 52) # speed 2AB
    PIIndex53 = tk.IntVar(vs_frame, value = 53) # switch 1
    PIIndex54 = tk.IntVar(vs_frame, value = 54) # open
    PIIndex55 = tk.IntVar(vs_frame, value = 55) # switch 2
    PIIndex56 = tk.IntVar(vs_frame, value = 56) # open
    PIIndex57 = tk.IntVar(vs_frame, value = 57) # switch 3
    PIIndex58 = tk.IntVar(vs_frame, value = 58) # open
    PIIndex59 = tk.IntVar(vs_frame, value = 59) # switch 4
    PIIndex60 = tk.IntVar(vs_frame, value = 60) # open
    PIIndex61 = tk.IntVar(vs_frame, value = 61) # switch 5
    PIIndex62 = tk.IntVar(vs_frame, value = 62) # open
    PIIndex63 = tk.IntVar(vs_frame, value = 63) # switch 6
    PIIndex64 = tk.IntVar(vs_frame, value = 64) # NOT USED #, HMI_TramQuietb
    PIIndex65 = tk.IntVar(vs_frame, value = 65) # TramStn1_HMIb
    PIIndex66 = tk.IntVar(vs_frame, value = 66) # TramStn2_HMIb
    PIIndex67 = tk.IntVar(vs_frame, value = 67) # TramStn3_HMIb
    PIIndex68 = tk.IntVar(vs_frame, value = 68) # TramStn4_HMIb
    PIIndex69 = tk.IntVar(vs_frame, value = 69) # TramStn5_HMIb
    PIIndex70 = tk.IntVar(vs_frame, value = 70) # TramStn6_HMIb
    PIIndex71 = tk.IntVar(vs_frame, value = 71) # open

    HMI_lbl0a = tk.Label(vs_frame,text="IND",justify="center",
                        width=4, borderwidth=1, relief="solid",font=('Times new roman',10,'bold'), bg="springgreen")
    HMI_lbl0a.grid(row=0, column = 0)
    HMI_lbl0b = tk.Label(vs_frame,text="TAG",justify="center",width=18, borderwidth=1, relief="solid",font=('Times new roman',10,'bold'))
    HMI_lbl0b.grid(row=0, column = 1)
    HMI_lbl0c = tk.Label(vs_frame,text="BTN",justify="center",width=6, borderwidth=1, relief="solid",font=('Times new roman',10,'bold'))
    HMI_lbl0c.grid(row=0, column = 2)
    HMI_lbl0d = tk.Label(vs_frame,text="Val",justify="center",width=6, borderwidth=1, relief="solid",font=('Times new roman',10,'bold'))
    HMI_lbl0d.grid(row=0, column = 3)
    PI_lbl0e = tk.Label(vs_frame,text="IND",justify="center",
                    width=4, borderwidth=1, relief="solid",font=('Times new roman',10,'bold'), bg="springgreen")
    PI_lbl0e.grid(row=0, column = 4)
    PI_lbl0f = tk.Label(vs_frame,text="TAG",justify="center",width=18, borderwidth=1, relief="solid",font=('Times new roman',10,'bold'))
    PI_lbl0f.grid(row=0, column = 5)
    PI_lbl0g = tk.Label(vs_frame,text="BTN",justify="center",width=6, borderwidth=1, relief="solid",font=('Times new roman',10,'bold'))
    PI_lbl0g.grid(row=0, column = 6)
    PI_lbl0h = tk.Label(vs_frame,text="Val",justify="center",width=10, borderwidth=1, relief="solid",font=('Times new roman',10,'bold')).grid(row=0, column = 7)
    time_string = strftime('%H:%M:%S')
    PI_lbl0i = tk.Label(vs_frame,text="TIME",justify="center",width=8, borderwidth=1, relief="solid",font=('Times new roman',10,'bold'))
    PI_lbl0i.grid(row=0, column = 8)
    timelbl=tk.Label(vs_frame,text=time_string,justify="center",width=7, borderwidth=1, relief="solid", font=('Digital-7',13),bg='purple', fg='white')
    timelbl.grid(row=1, column = 8)

    HMI_lbl1a = tk.Label(vs_frame,text="--",justify="center",width=6, borderwidth=1, relief="solid")
    HMI_lbl1a.grid(row=1, column = 0)
    HMI_lbl1b = tk.Label(vs_frame,text="RR1ABspeed_HMI",justify="center",width=20, borderwidth=1, relief="solid").grid(row=1, column =1)
    HMI_lbl1c = tk.Button(vs_frame,text="--",justify="center",width=8,borderwidth=1, relief="solid" ,pady=0)
    HMI_lbl1c.grid(row=1, column = 2)
    HMI_lbl1d = tk.Label(vs_frame,text=UpdateSpeed1a,justify="center",width=10, borderwidth=1, relief="solid")
    HMI_lbl1d.grid(row=1, column = 3)
    HMI_lbl2a = tk.Label(vs_frame,text="--",justify="center",width=6, borderwidth=1, relief="solid")
    HMI_lbl2a.grid(row=2, column = 0)
    HMI_lbl2b = tk.Label(vs_frame,text="RR1CDspeed_HMI",justify="center",width=20, borderwidth=1, relief="solid")
    HMI_lbl2b.grid(row=2, column =1)
    HMI_lbl2c = tk.Button(vs_frame,text="--",justify="center",width=8,height=1,borderwidth=1, relief="solid",pady=0)
    HMI_lbl2c.grid(row=2, column = 2)
    HMI_lbl2d = tk.Label(vs_frame,text=UpdateSpeed1c,justify="center",width=10, borderwidth=1, relief="solid")
    HMI_lbl2d.grid(row=2, column = 3)

    HMI_lbl3a = tk.Label(vs_frame,text="--",justify="center",width=6, borderwidth=1, relief="solid")
    HMI_lbl3a.grid(row=3, column = 0)
    HMI_lbl3b = tk.Label(vs_frame,text="RR2ABspeed_HMI",justify="center",width=20, borderwidth=1, relief="solid")
    HMI_lbl3b.grid(row=3, column =1)
    HMI_lbl3c = tk.Button(vs_frame,text="--",justify="center",width=8,borderwidth=1, relief="solid",pady=0)
    HMI_lbl3c.grid(row=3, column = 2)
    HMI_lbl3d = tk.Label(vs_frame,text=UpdateSpeed2a,justify="center",width=10, borderwidth=1, relief="solid")
    HMI_lbl3d.grid(row=3, column = 3)

    HMI_lbl4a = tk.Label(vs_frame,textvariable=HMIIndex01,justify="center",width=6, borderwidth=1, relief="solid")
    HMI_lbl4a.grid(row=4, column = 0)
    HMI_lbl4b = tk.Label(vs_frame,text="HMI_RHT",justify="center",width=20, borderwidth=1, relief="solid")
    HMI_lbl4b.grid(row=4, column =1)
    HMI_lbl4c = tk.Button(vs_frame,text="Click",justify="center",width=8,borderwidth=1, relief="solid",bg="lightgoldenrod",
                        command=lambda:HMI_Interface(1,HMIIndex01.get(),HMI_spin4d.get()),pady=0)
    HMI_lbl4c.grid(row=4, column = 2)
    HMI_spin4d = tk.Spinbox(vs_frame, from_=10, to=25,increment=1.0,justify="center",width=8)
    HMI_spin4d.grid(row=4, column = 3)
    HMI_lbl5a = tk.Label(vs_frame,textvariable=HMIIndex02,justify="center",width=6, borderwidth=1, relief="solid")
    HMI_lbl5a.grid(row=5, column = 0)
    HMI_lbl5b = tk.Label(vs_frame,text="HMI_TramStopTime",justify="center",width=20, borderwidth=1, relief="solid")
    HMI_lbl5b.grid(row=5, column =1)
    HMI_btn5c = tk.Button(vs_frame,text="Click",justify="center",width=8,borderwidth=1,pady=0,relief="solid",bg="lightgoldenrod",
                        command=lambda:HMI_Interface(1,HMIIndex02.get(),HMI_spin5d.get()))
    HMI_btn5c.grid(row=5, column = 2)
    HMI_spin5d = tk.Spinbox(vs_frame, from_=5, to=55,increment=1,justify="center",width=8)
    HMI_spin5d.grid(row=5, column = 3)

    HMI_lbl6a = tk.Label(vs_frame,textvariable=HMIIndex03,justify="center",width=6, borderwidth=1, relief="solid")
    HMI_lbl6a.grid(row=6, column = 0)
    HMI_lbl6b = tk.Label(vs_frame,text="HMI_AllQuietb",justify="center",width=20, borderwidth=1, relief="solid")
    HMI_lbl6b.grid(row=6, column =1)
    HMI_btn6c = tk.Button(vs_frame,text="Snd/Quite",justify="center",width=8,borderwidth=1, relief="solid",bg="lightgoldenrod",pady=0,
                        command=lambda:HMI_PB(1,HMIIndex03.get(),2))
    HMI_btn6c.grid(row=6, column = 2)
    HMI_lbl6d = tk.Label(vs_frame,text=False,justify="center",width=8, borderwidth=1, relief="solid")
    HMI_lbl6d.grid(row=6, column = 3)

    HMI_lbl7a = tk.Label(vs_frame,textvariable=HMIIndex04,justify="center",width=6, borderwidth=1, relief="solid")
    HMI_lbl7a.grid(row=7, column = 0)
    HMI_lbl7b = tk.Label(vs_frame,text="HMI_LIGHTONOFFb",justify="center",width=20, borderwidth=1, relief="solid")
    HMI_lbl7b.grid(row=7, column =1)
    HMI_btn7c = tk.Button(vs_frame,text="Lights",justify="center",width=8,borderwidth=1, relief="solid",bg="lightgoldenrod",
                        command=lambda:HMI_PB(1,HMIIndex04.get(),2),pady=0)
    HMI_btn7c.grid(row=7, column = 2)
    HMI_lbl7d = tk.Label(vs_frame,text=False,justify="center",width=8, borderwidth=1, relief="solid")
    HMI_lbl7d.grid(row=7, column = 3)

    HMI_lbl8a = tk.Label(vs_frame,textvariable=HMIIndex05,justify="center",width=6, borderwidth=1, relief="solid")
    HMI_lbl8a.grid(row=8, column = 0)
    HMI_lbl8b = tk.Label(vs_frame,text="HMI_RR2_RR3Pwrb",justify="center",width=20, borderwidth=1, relief="solid")
    HMI_lbl8b.grid(row=8, column =1)
    HMI_btn8c = tk.Button(vs_frame,text="RR2/RR3 Pwr",justify="center",pady=0,width=8,borderwidth=1, relief="solid",bg="lightgoldenrod",
                        command=lambda:HMI_PB(1,HMIIndex05.get(),2))
    HMI_btn8c.grid(row=8, column = 2)
    HMI_lbl8d = tk.Label(vs_frame,text=False,justify="center",width=8, borderwidth=1, relief="solid")
    HMI_lbl8d.grid(row=8, column = 3)

    HMI_lbl9a = tk.Label(vs_frame,textvariable=HMIIndex06,justify="center",width=6, borderwidth=1, relief="solid")
    HMI_lbl9a.grid(row=9, column = 0)
    HMI_lbl9b = tk.Label(vs_frame,text="HMI_RRBellb",justify="center",width=20, borderwidth=1, relief="solid")
    HMI_lbl9b.grid(row=9, column =1)
    HMI_btn9c = tk.Button(vs_frame,text="Flip",pady=0,justify="center",width=8,borderwidth=1, relief="solid",bg="lightgoldenrod",
                        command=lambda:HMI_PB(1,HMIIndex06.get(),2))
    HMI_btn9c.grid(row=9, column = 2)
    HMI_lbl9d = tk.Label(vs_frame,text=False,justify="center",width=8, borderwidth=1, relief="solid")
    HMI_lbl9d.grid(row=9, column = 3)

    HMI_lbl10a = tk.Label(vs_frame,textvariable=HMIIndex07,justify="center",width=6, borderwidth=1, relief="solid")
    HMI_lbl10a.grid(row=10, column = 0)
    HMI_lbl10b = tk.Label(vs_frame,text="HMI_RRDieselSteamb",justify="center",width=20, borderwidth=1, relief="solid")
    HMI_lbl10b.grid(row=10, column =1)
    HMI_btn10c = tk.Button(vs_frame,text="Flip",pady=0,justify="center",width=8,borderwidth=1, relief="solid",bg="lightgoldenrod",
                        command=lambda:HMI_PB(1,HMIIndex07.get(),2))
    HMI_btn10c.grid(row=10, column = 2)
    HMI_lbl10d = tk.Label(vs_frame,text=False,justify="center",width=8, borderwidth=1, relief="solid")
    HMI_lbl10d.grid(row=10, column = 3)

    HMI_lbl11a = tk.Label(vs_frame,textvariable=HMIIndex08,justify="center",width=6, borderwidth=1, relief="solid")
    HMI_lbl11a.grid(row=11, column = 0)
    HMI_lbl11b = tk.Label(vs_frame,text="HMI_RRHornb",justify="center",width=20, borderwidth=1, relief="solid")
    HMI_lbl11b.grid(row=11, column =1)
    HMI_btn11c = tk.Button(vs_frame,text="Horn/Quite",justify="center",width=8,borderwidth=1, relief="solid",bg="lightgoldenrod",
                        command=lambda:HMI_PB(1,HMIIndex08.get(),2),pady=0)
    HMI_btn11c.grid(row=11, column = 2)
    HMI_lbl11d = tk.Label(vs_frame,text=False,justify="center",width=8, borderwidth=1, relief="solid")
    HMI_lbl11d.grid(row=11, column = 3)

    HMI_lbl12a = tk.Label(vs_frame,textvariable=HMIIndex09,justify="center",width=6, borderwidth=1, relief="solid")
    HMI_lbl12a.grid(row=12, column = 0)
    HMI_lbl12b = tk.Label(vs_frame,text="HMI_RRQuiteb",justify="center",width=20, borderwidth=1, relief="solid")
    HMI_lbl12b.grid(row=12, column =1)
    HMI_btn12c = tk.Button(vs_frame,text="Flip",justify="center",width=8,borderwidth=1, relief="solid",bg="lightgoldenrod",
                        command=lambda:HMI_PB(1,HMIIndex09.get(),2),pady=0)
    HMI_btn12c.grid(row=12, column = 2)
    HMI_lbl12d = tk.Label(vs_frame,text=False,justify="center",width=8, borderwidth=1, relief="solid",font=('Times new roman',11,'normal'))
    HMI_lbl12d.grid(row=12, column = 3)

    HMI_lbl13a = tk.Label(vs_frame,textvariable=HMIIndex10,justify="center",width=6, borderwidth=1, relief="solid")
    HMI_lbl13a.grid(row=13, column = 0)
    HMI_lbl13b = tk.Label(vs_frame,text="HMI_RRWhistleb",justify="center",width=20, borderwidth=1, relief="solid")
    HMI_lbl13b.grid(row=13, column =1)
    HMI_btn13c = tk.Button(vs_frame,text="Flip",justify="center",width=8,pady=0,borderwidth=1, relief="solid",bg="lightgoldenrod",
                        command=lambda:HMI_PB(1,HMIIndex10.get(),2))
    HMI_btn13c.grid(row=13, column = 2)
    HMI_lbl13d = tk.Label(vs_frame,text=False,justify="center",width=8, borderwidth=1, relief="solid")
    HMI_lbl13d.grid(row=13, column = 3)

    HMI_lbl14a = tk.Label(vs_frame,textvariable=HMIIndex11,justify="center",width=6, borderwidth=1, relief="solid")
    HMI_lbl14a.grid(row=10, column = 0)
    HMI_lbl14b = tk.Label(vs_frame,text="HMI_Switch1ABb",justify="center",width=20, borderwidth=1, relief="solid")
    HMI_lbl14b.grid(row=10, column =1)
    HMI_btn14c = tk.Button(vs_frame,text="==/Connect",justify="center",width=8,pady=0,borderwidth=1, relief="solid",bg="lightgoldenrod",
                        command=lambda:HMI_PB(1,HMIIndex11.get(),2))
    HMI_btn14c.grid(row=10, column = 2)
    HMI_lbl14d = tk.Label(vs_frame,text=False,justify="center",width=8, borderwidth=1, relief="solid")
    HMI_lbl14d.grid(row=10, column = 3)

    HMI_lbl15a = tk.Label(vs_frame,textvariable=HMIIndex12,justify="center",width=6, borderwidth=1, relief="solid")
    HMI_lbl15a.grid(row=15, column = 0)
    HMI_lbl15b = tk.Label(vs_frame,text="HMI_Switch2RR3b",justify="center",width=20, borderwidth=1, relief="solid")
    HMI_lbl15b.grid(row=15, column =1)
    HMI_btn15c = tk.Button(vs_frame,text="==/Connect",justify="center",width=8,pady=0,borderwidth=1, relief="solid",bg="lightgoldenrod",
                        command=lambda:HMI_PB(1,HMIIndex12.get(),2))
    HMI_btn15c.grid(row=15, column = 2)
    HMI_lbl15d = tk.Label(vs_frame,text=False,justify="center",width=8, borderwidth=1, relief="solid")
    HMI_lbl15d.grid(row=15, column = 3)

    HMI_lbl16a = tk.Label(vs_frame,textvariable=HMIIndex13,justify="center",width=6, borderwidth=1, relief="solid")
    HMI_lbl16a.grid(row=16, column = 0)
    HMI_lbl16b = tk.Label(vs_frame,text="HMI_Switch3RR4b",justify="center",width=20, borderwidth=1, relief="solid")
    HMI_lbl16b.grid(row=16, column =1)
    HMI_btn16c = tk.Button(vs_frame,text="==/Connect",justify="center",width=8,pady=0,borderwidth=1, relief="solid",bg="lightgoldenrod",
                        command=lambda:HMI_PB(1,HMIIndex13.get(),2))
    HMI_btn16c.grid(row=16, column = 2)
    HMI_lbl16d = tk.Label(vs_frame,text=False,justify="center",width=8, borderwidth=1, relief="solid")
    HMI_lbl16d.grid(row=16, column = 3)

    HMI_lbl17a = tk.Label(vs_frame,textvariable=HMIIndex14,justify="center",width=6, borderwidth=1, relief="solid")
    HMI_lbl17a.grid(row=17, column = 0)
    HMI_lbl17b = tk.Label(vs_frame,text="HMI_Switch4RR3b",justify="center",width=20, borderwidth=1, relief="solid")
    HMI_lbl17b.grid(row=17, column =1)
    HMI_btn17c = tk.Button(vs_frame,text="==/Connect",justify="center",width=8,pady=0,borderwidth=1, relief="solid",bg="lightgoldenrod",
                        command=lambda:HMI_PB(1,HMIIndex14.get(),2))
    HMI_btn17c.grid(row=17, column = 2)
    HMI_lbl17d = tk.Label(vs_frame,text=False,justify="center",width=8, borderwidth=1, relief="solid")
    HMI_lbl17d.grid(row=17, column = 3)

    HMI_lbl18a = tk.Label(vs_frame,textvariable=HMIIndex15,justify="center",width=6, borderwidth=1, relief="solid")
    HMI_lbl18a.grid(row=18, column = 0)
    HMI_lbl18b = tk.Label(vs_frame,text="HMI_Switch5ABb",justify="center",width=20, borderwidth=1, relief="solid")
    HMI_lbl18b.grid(row=18, column =1)
    HMI_btn18c = tk.Button(vs_frame,text="==/Connect",justify="center",width=8,pady=0,borderwidth=1, relief="solid",bg="lightgoldenrod",
                        command=lambda:HMI_PB(1,HMIIndex15.get(),2))
    HMI_btn18c.grid(row=18, column = 2)
    HMI_lbl18d = tk.Label(vs_frame,text=False,justify="center",width=8, borderwidth=1, relief="solid")
    HMI_lbl18d.grid(row=18, column = 3)

    HMI_lbl19a = tk.Label(vs_frame,textvariable=HMIIndex16,justify="center",width=6, borderwidth=1, relief="solid")
    HMI_lbl19a.grid(row=19, column = 0)
    HMI_lbl19b = tk.Label(vs_frame,text="HMI_Switch6ABb",justify="center",width=20, borderwidth=1, relief="solid")
    HMI_lbl19b.grid(row=19, column =1)
    HMI_btn19c = tk.Button(vs_frame,text="==/Connect",justify="center",width=8,pady=0,borderwidth=1, relief="solid",bg="lightgoldenrod",
                        command=lambda:HMI_PB(1,HMIIndex16.get(),2))
    HMI_btn19c.grid(row=19, column = 2)
    HMI_lbl19d = tk.Label(vs_frame,text=False,justify="center",width=8, borderwidth=1, relief="solid")
    HMI_lbl19d.grid(row=19, column = 3)

    HMI_lbl20a = tk.Label(vs_frame,textvariable=HMIIndex17,justify="center",width=6, borderwidth=1, relief="solid")
    HMI_lbl20a.grid(row=20, column = 0) # HMI_TramQuietb, no feedback
    HMI_lbl20b = tk.Label(vs_frame,text="HMI_TramQuietb",justify="center",width=20, borderwidth=1, relief="solid")
    HMI_lbl20b.grid(row=20, column =1)
    HMI_btn20c = tk.Button(vs_frame,text="Trm/No SND",justify="center",width=8,pady=0,borderwidth=1, relief="solid",bg="lightgoldenrod",
                        command=lambda:HMI_PB(1,HMIIndex17.get(),2))
    HMI_btn20c.grid(row=20, column = 2)
    HMI_lbl20d = tk.Label(vs_frame,text="False",justify="center",width=8, borderwidth=1, relief="solid")
    HMI_lbl20d.grid(row=20, column = 3)
    # Station 1
    HMI_lbl21a = tk.Label(vs_frame,text="--",justify="center",width=6, borderwidth=1, relief="solid",padx=0)
    HMI_lbl21a.grid(row=21, column = 0,padx=0) # Tram at station 1, no HMI #
    HMI_lbl21b = tk.Label(vs_frame,text="TramStn1_HMIb",justify="center",width=20, borderwidth=1, relief="solid",padx=0)
    HMI_lbl21b.grid(row=21, column =1,padx=0)
    HMI_btn21c = tk.Button(vs_frame,text="must stop",justify="center",width=8,pady=0,borderwidth=1, relief="solid",bg="yellowgreen",padx=0)
    HMI_btn21c.grid(row=21, column = 2,padx=0)
    HMI_lbl21d = tk.Label(vs_frame,text=False,justify="center",width=8, borderwidth=1, relief="solid",padx=0)
    HMI_lbl21d.grid(row=21, column = 3)
    # Station 2
    HMI_lbl22a = tk.Label(vs_frame,textvariable=HMIIndex18,justify="center",width=6, borderwidth=1, relief="solid")
    HMI_lbl22a.grid(row=22, column = 0)
    HMI_lbl22b = tk.Label(vs_frame,text="HMI_TramStpStn_2b",justify="center",width=20, borderwidth=1, relief="solid")
    HMI_lbl22b.grid(row=22, column =1)
    HMI_btn22c = tk.Button(vs_frame,text="Bypass/Stop",justify="center",width=8,pady=0,borderwidth=1,relief="solid",bg="lightgoldenrod",
                        command=lambda:HMI_PB(1,HMIIndex18.get(),2))
    HMI_btn22c.grid(row=22, column = 2)
    HMI_lbl22d = tk.Label(vs_frame,text=False,justify="center",width=8, borderwidth=1, relief="solid")
    HMI_lbl22d.grid(row=22, column = 3)
    # Station 3
    HMI_lbl23a = tk.Label(vs_frame,textvariable=HMIIndex19,justify="center",width=6, borderwidth=1, relief="solid")
    HMI_lbl23a.grid(row=23, column = 0)
    HMI_lbl23b = tk.Label(vs_frame,text="HMI_TramStpStn_3b",justify="center",width=20, borderwidth=1, relief="solid")
    HMI_lbl23b.grid(row=23, column =1)
    HMI_btn23c = tk.Button(vs_frame,text="Bypass/Stop",justify="center",width=8,pady=0,borderwidth=1, relief="solid",bg="lightgoldenrod",
                        command=lambda:HMI_PB(1,HMIIndex19.get(),2))
    HMI_btn23c.grid(row=23, column = 2)
    HMI_lbl23d = tk.Label(vs_frame,text=False,justify="center",width=8, borderwidth=1, relief="solid")
    HMI_lbl23d.grid(row=23, column = 3)
    # Station 4
    HMI_lbl24a = tk.Label(vs_frame,text="--",justify="center",width=6, borderwidth=1, relief="solid")
    HMI_lbl24a.grid(row=24, column = 0)  
    HMI_lbl24b = tk.Label(vs_frame,text="TramStn4_HMIb",justify="center",width=20, borderwidth=1, relief="solid")
    HMI_lbl24b.grid(row=24, column =1)
    HMI_btn24c = tk.Button(vs_frame,text="must stop",justify="center",width=8,pady=0,borderwidth=1, relief="solid",bg="yellowgreen")
    HMI_btn24c.grid(row=24, column = 2)
    HMI_lbl24d = tk.Label(vs_frame,text=False,justify="center",width=8, borderwidth=1, relief="solid")
    HMI_lbl24d.grid(row=24, column = 3)
    # Station 5
    HMI_lbl25a = tk.Label(vs_frame,textvariable=HMIIndex20,justify="center",width=6, borderwidth=1, relief="solid")
    HMI_lbl25a.grid(row=25, column = 0)
    HMI_lbl25b = tk.Label(vs_frame,text="HMI_TramStpStn_5b",justify="center",width=20, borderwidth=1, relief="solid")
    HMI_lbl25b.grid(row=25, column =1)
    HMI_btn25c = tk.Button(vs_frame,text="Bypass/Stop",justify="center",width=8,pady=0,borderwidth=1, relief="solid",bg="lightgoldenrod",
                        command=lambda:HMI_PB(1,HMIIndex20.get(),2))
    HMI_btn25c.grid(row=25, column = 2)
    HMI_lbl25d = tk.Label(vs_frame,text=False,justify="center",width=8, borderwidth=1, relief="solid")
    HMI_lbl25d.grid(row=25, column = 3)
    # Station 6
    HMI_lbl26a = tk.Label(vs_frame,textvariable=HMIIndex21,justify="center",width=6, borderwidth=1, relief="solid")
    HMI_lbl26a.grid(row=26, column = 0)
    HMI_lbl26b = tk.Label(vs_frame,text="HMI_TramStpStn_6b",justify="center",width=20, borderwidth=1, relief="solid")
    HMI_lbl26b.grid(row=26, column =1)
    HMI_btn26c = tk.Button(vs_frame,text="Bypass/Stop",justify="center",width=8,pady=0,borderwidth=1, relief="solid",bg="lightgoldenrod",
                        command=lambda:HMI_PB(1,HMIIndex21.get(),2))
    HMI_btn26c.grid(row=26, column = 2)
    HMI_lbl26d = tk.Label(vs_frame,text=False,justify="center",width=8, borderwidth=1, relief="solid")
    HMI_lbl26d.grid(row=26, column = 3)

    # PI Below
    PI_lbl1e = tk.Label(vs_frame,text=50,justify="center",width=6, borderwidth=3,relief="solid")
    PI_lbl1e.grid(row=1, column = 4)
    PI_lbl1f = tk.Label(vs_frame,text="RR1ABspeed_HMI",justify="center",width=20, borderwidth=1, relief="solid")
    PI_lbl1f.grid(row=1, column =5)
    PI_btn1g = tk.Button(vs_frame,text="Click",justify="center",width=8,pady=0,borderwidth=1, bg="lightgoldenrod",
                        relief="raised",command=lambda:HMI_Interface(1,PIIndex50.get(),PI_ent1h.get()))
    PI_btn1g.grid(row=1, column = 6)
    #Define entry for speed & validate
    PI_ent1h = tk.Spinbox(vs_frame, from_=0.1, to=75.4,increment=0.5,justify="center",width=8) #tk.Entry(vs_frame,justify="center",width=10,borderwidth=3, relief="solid",bg="lightgrey",font=('Times new roman',11,'bold')                   
    PI_ent1h.grid(row=1, column = 7)
    PI_lbl2e = tk.Label(vs_frame,textvariable=PIIndex51,justify="center",width=6, borderwidth=3,relief="solid")
    PI_lbl2e.grid(row=2, column = 4)
    PI_lbl2f = tk.Label(vs_frame,text="RR1CDspeed_HMI",justify="center",width=20, borderwidth=1, relief="solid")
    PI_lbl2f.grid(row=2, column =5)
    PI_btn2g = tk.Button(vs_frame,text="Click",justify="center",width=8,pady=0,borderwidth=1, bg="lightgoldenrod",relief="raised", 
                        command=lambda:HMI_Interface(1,PIIndex51.get(),PI_ent2h.get()))
    PI_btn2g.grid(row=2, column = 6)
    PI_ent2h = tk.Spinbox(vs_frame, from_=0.2, to=75.4,increment=0.5,justify="center",width=8) 
    PI_ent2h.grid(row=2, column = 7)
    PI_lbl3e = tk.Label(vs_frame,textvariable=PIIndex52,
                        justify="center",width=6, borderwidth=3,relief="solid")
    PI_lbl3e.grid(row=3, column = 4)
    PI_lbl3f = tk.Label(vs_frame,text="RR2ABspeed_HMI",justify="center",width=20, borderwidth=1, relief="solid")
    PI_lbl3f.grid(row=3, column =5)
    PI_btn3g = tk.Button(vs_frame,text="Click",justify="center",width=8,pady=0,borderwidth=1,bg="lightgoldenrod",
                        relief="raised",command=lambda:HMI_Interface(1,PIIndex52.get(),PI_ent3h.get()))
    PI_btn3g.grid(row=3, column = 6)
    PI_ent3h = tk.Spinbox(vs_frame, from_=0.3, to=75.4,increment=0.5,justify="center",width=8)
    PI_ent3h.grid(row=3, column = 7)
    PI_lbl4e = tk.Label(vs_frame,text="--",justify="center",width=6, borderwidth=3,relief="solid")
    PI_lbl4e.grid(row=4, column = 4)
    PI_lbl4f = tk.Label(vs_frame,text="HMI_RHT",justify="center",width=20, borderwidth=1, relief="solid")
    PI_lbl4f.grid(row=4, column =5)
    PI_ent4g = tk.Button(vs_frame, text="--",width=8,borderwidth=1,pady=0,bg="lightgrey",
                        relief="raised") #= tk.Entry(vs_frame,justify="center",width=10,borderwidth=3, relief="solid",bg="lightgrey",font = ('Times new roman',10,'bold'), validate='key')
    PI_ent4g.grid(row=4, column = 6)
    PI_lbl4h = tk.Label(vs_frame,text=UpdateHMIRHT,justify="center",width=10, borderwidth=1, relief="solid")
    PI_lbl4h.grid(row=4, column = 7)

    PI_lbl5e = tk.Label(vs_frame,text="--",justify="center",width=6, borderwidth=3,relief="solid")
    PI_lbl5e.grid(row=5, column = 4)
    PI_lbl5f = tk.Label(vs_frame,text="HMI_TramStopTime",justify="center",width=20, borderwidth=1, relief="solid")
    PI_lbl5f.grid(row=5, column =5)
    PI_ent5g = tk.Button(vs_frame, text="--",width=8,borderwidth=1,pady=0,bg="lightgrey",
                        relief="raised") 
    PI_ent5g.grid(row=5, column = 6)
    PI_lbl5h = tk.Label(vs_frame,text=UpdateHMI_TramStopTime,justify="center",width=10, borderwidth=1, relief="solid")
    PI_lbl5h.grid(row=5, column = 7)
    PI_lbl6e = tk.Label(vs_frame,text="--",justify="center",width=6, borderwidth=3,relief="solid")
    PI_lbl6e.grid(row=6, column = 4)
    PI_lbl6f = tk.Label(vs_frame,text="HMI_AllQuietb",justify="center",width=20, borderwidth=1, relief="solid")
    PI_lbl6f.grid(row=6, column =5)
    PI_ent6g = tk.Button(vs_frame, text="--",width=8,borderwidth=1,pady=0,bg="lightgrey",
                        relief="raised") 
    PI_ent6g.grid(row=6, column = 6)
    PI_lbl6h = tk.Label(vs_frame,text=HMI_PB,justify="center",width=10, borderwidth=1, relief="solid")
    PI_lbl6h.grid(row=6, column = 7)
    PI_lbl7e = tk.Label(vs_frame,text="--",justify="center",width=6, borderwidth=3,relief="solid")
    PI_lbl7e.grid(row=7, column = 4)
    PI_lbl7f = tk.Label(vs_frame,text="HMI_LIGHTONOFFb",justify="center",width=20, borderwidth=1, relief="solid")
    PI_lbl7f.grid(row=7, column =5)
    PI_ent7g = tk.Button(vs_frame, text="--",width=8,borderwidth=1,pady=0,bg="lightgrey",
                        relief="raised") 
    PI_ent7g.grid(row=7, column = 6)
    PI_lbl7h = tk.Label(vs_frame,text=HMI_PB,justify="center",width=10, borderwidth=1, relief="solid")
    PI_lbl7h.grid(row=7, column = 7)

    PI_lbl8e = tk.Label(vs_frame,text="--",justify="center",width=6, borderwidth=3,relief="solid")
    PI_lbl8e.grid(row=8, column = 4)
    PI_lbl8f = tk.Label(vs_frame,text="HMI_RR2_RR3Pwrb",justify="center",width=20, borderwidth=1, relief="solid")
    PI_lbl8f.grid(row=8, column =5)
    PI_ent8g = tk.Button(vs_frame, text="--",width=8,borderwidth=1,pady=0,bg="lightgrey",
                        relief="raised") 
    PI_ent8g.grid(row=8, column = 6)
    PI_lbl8h = tk.Label(vs_frame,text=HMI_PB,justify="center",width=10, borderwidth=1, relief="solid")
    PI_lbl8h.grid(row=8, column = 7)

    PI_lbl9e = tk.Label(vs_frame,text="--",justify="center",width=6, borderwidth=3,relief="solid")
    PI_lbl9e.grid(row=9, column = 4)
    PI_lbl9f = tk.Label(vs_frame,text="HMI_RRBellb",justify="center",width=20, borderwidth=1, relief="solid")
    PI_lbl9f.grid(row=9, column =5)
    PI_ent9g = tk.Button(vs_frame, text="--",width=8,borderwidth=1,pady=0,bg="lightgrey",
                        relief="raised") 
    PI_ent9g.grid(row=9, column = 6)
    PI_lbl9h = tk.Label(vs_frame,text=HMI_PB,justify="center",width=10, borderwidth=1, relief="solid")
    PI_lbl9h.grid(row=9, column = 7)

    PI_lbl10e = tk.Label(vs_frame,text="--",justify="center",width=6, borderwidth=3,relief="solid")
    PI_lbl10e.grid(row=10, column = 4)
    PI_lbl10f = tk.Label(vs_frame,text="HMI_RRDieselSteamb",justify="center",width=20, borderwidth=1, relief="solid")
    PI_lbl10f.grid(row=10, column =5)
    PI_ent10g = tk.Button(vs_frame, text="--",width=8,borderwidth=1,pady=0,bg="lightgrey",
                        relief="raised") 
    PI_ent10g.grid(row=10, column = 6)
    PI_lbl10h = tk.Label(vs_frame,text=HMI_PB,justify="center",width=10, borderwidth=1, relief="solid")
    PI_lbl10h.grid(row=10, column = 7)

    PI_lbl11e = tk.Label(vs_frame,text="--",justify="center",width=6, borderwidth=3,relief="solid")
    PI_lbl11e.grid(row=11, column = 4)
    PI_lbl11f = tk.Label(vs_frame,text="HMI_RRHornb",justify="center",width=20, borderwidth=1, relief="solid")
    PI_lbl11f.grid(row=11, column =5)
    PI_ent11g = tk.Button(vs_frame, text="--",width=8,borderwidth=1,pady=0,bg="lightgrey",
                        relief="raised") 
    PI_ent11g.grid(row=11, column = 6)
    PI_lbl11h = tk.Label(vs_frame,text=HMI_PB,justify="center",width=10, borderwidth=1, relief="solid")
    PI_lbl11h.grid(row=11, column = 7)

    PI_lbl12e = tk.Label(vs_frame,text="--",justify="center",width=6, borderwidth=3,relief="solid")
    PI_lbl12e.grid(row=12, column = 4)
    PI_lbl12f = tk.Label(vs_frame,text="HMI_RRQuietb",justify="center",width=20, borderwidth=1, relief="solid")
    PI_lbl12f.grid(row=12, column =5)
    PI_ent12g = tk.Button(vs_frame, text="--",width=8,borderwidth=1,pady=0,bg="lightgrey",
                        relief="raised") 
    PI_ent12g.grid(row=12, column = 6)
    PI_lbl12h = tk.Label(vs_frame,text=HMI_PB,justify="center",width=10, borderwidth=1, relief="solid",pady=0)
    PI_lbl12h.grid(row=12, column = 7)

    PI_lbl13e = tk.Label(vs_frame,text="--",justify="center",width=6, borderwidth=3,relief="solid")
    PI_lbl13e.grid(row=13, column = 4)
    PI_lbl13f = tk.Label(vs_frame,text="HMI_RRWhistleb",justify="center",width=20, borderwidth=1, relief="solid")
    PI_lbl13f.grid(row=13, column=5)
    PI_ent13g = tk.Button(vs_frame, text="--",width=8,borderwidth=1,pady=0,bg="lightgrey",
                        relief="raised") 
    PI_ent13g.grid(row=13, column = 6)
    PI_lbl13h = tk.Label(vs_frame,text=HMI_PB,justify="center",width=10, borderwidth=1, relief="solid")
    PI_lbl13h.grid(row=13, column = 7)

    PI_lbl14e = tk.Label(vs_frame,textvariable=PIIndex53,justify="center",width=6, borderwidth=3,relief="solid")
    PI_lbl14e.grid(row=10, column = 4)
    PI_lbl14f = tk.Label(vs_frame,text="Swtch1Main_HMIb fdbck",justify="center",width=20, borderwidth=1, relief="solid")
    PI_lbl14f.grid(row=10, column =5)
    PI_btn14g = tk.Button(vs_frame,text=UpdatePISwitch1,justify="center",width=8,borderwidth=1,
                          bg="lightgrey",pady=0,relief="raised",
                          command=lambda:UpdateSwitchFdBck(1,PIIndex53.get(),1)) 
    PI_btn14g.grid(row=10, column = 6)
    PI_lbl14h = tk.Label(vs_frame,text=HMI_PB,justify="center",width=10, borderwidth=1, relief="solid")
    PI_lbl14h.grid(row=10, column = 7)
    PI_lbl14i = tk.Label(vs_frame,text="Grn=True, Red=False",justify="center",width=20, borderwidth=1, relief="solid")
    PI_lbl14i.grid(row=10, column = 8)
    PI_lbl14ia = tk.Label(vs_frame,text="Grn=True, Red=False",justify="center",width=20, borderwidth=1, relief="solid")
    PI_lbl14ia.grid(row=15, column = 8)

    PI_lbl15e = tk.Label(vs_frame,textvariable=PIIndex55,justify="center",width=6, borderwidth=3,relief="solid")
    PI_lbl15e.grid(row=15, column = 4)
    PI_lbl15f = tk.Label(vs_frame,text="Swtch2RR3Main_HMIb fdbck",justify="center",width=20, borderwidth=1, relief="solid")
    PI_lbl15f.grid(row=15, column =5)
    PI_btn15g = tk.Button(vs_frame,text=UpdatePISwitch1,justify="center",width=8,borderwidth=1,bg="lightgrey",pady=0,relief="raised",
                          command = lambda:UpdateSwitchFdBck(1,PIIndex55.get(),1)) 
    PI_btn15g.grid(row=15, column = 6)
    PI_lbl15h = tk.Label(vs_frame,text=HMI_PB,justify="center",width=10, borderwidth=1, relief="solid")
    PI_lbl15h.grid(row=15, column = 7)

    AutoFlipbtn=tk.Checkbutton(vs_frame,text="AutoFeedback?",variable=AutoFlipValueb,onvalue=True,offvalue=False,
                               justify="center",width=18,borderwidth=1,bg="lightgrey",
                               relief="raised",command=lambda:HMI_PB(0,99,AutoFlipspin.get()))
    AutoFlipbtn.grid(row=16, column = 8)
    var = tk.DoubleVar(vs_frame)
    var.set(5.0) # switchfeedback time delay  HMI sends cmd, delay, GUI program sets fdbck bit
    var1 = 0.500 # server update time delay
    AutoFlipspin=tk.Spinbox(vs_frame, from_=0.50,to=10.00,increment=0.5,textvariable=var,
                            justify="center",width=12,format="%.02f",font=('Times new roman',18,'bold'))
    AutoFlipspin.grid(row=17, column = 8)    
    Autotxt1=tk.Label(vs_frame,text="Delay, sec",justify="center",width=12,borderwidth=1,bg="lightgrey",relief="raised")
    Autotxt1.grid(row=16, column = 9)
    Autotxt2=tk.Label(vs_frame,text="0.500 to 10,+/-0.5",justify="center",width=15,borderwidth=1,bg="lightgrey",relief="raised",font=('Times new roman',11,'bold'))
    Autotxt2.grid(row=17, column = 9)
    AutoFliplbl=tk.Label(vs_frame,text="select",borderwidth=1,relief="solid",justify="center",width=18, font=('Times new roman',12,'bold'),bg="lightgrey")
    AutoFliplbl.grid(row=18, column = 8)

    PI_lbl16e = tk.Label(vs_frame,textvariable=PIIndex57,justify="center",width=6, borderwidth=3,relief="solid")
    PI_lbl16e.grid(row=16, column = 4)
    PI_lbl16f = tk.Label(vs_frame,text="Swtch3RR4Main_HMIb fdbck",justify="center",width=20, borderwidth=1, relief="solid")
    PI_lbl16f.grid(row=16, column =5)
    PI_btn16g = tk.Button(vs_frame,text=UpdatePISwitch1,pady=0,justify="center",width=8,borderwidth=1,bg="lightgrey",relief="raised",
                         command=lambda:UpdateSwitchFdBck(1,PIIndex57.get(),1)) 
    PI_btn16g.grid(row=16, column = 6)
    PI_btn16h = tk.Button(vs_frame,text=HMI_PB,pady=0,padx=0,justify="center",width=10, borderwidth=1, relief="solid")
    PI_btn16h.grid(row=16, column = 7)

    PI_lbl17e = tk.Label(vs_frame,textvariable=PIIndex59,justify="center",width=6, borderwidth=3,relief="solid")
    PI_lbl17e.grid(row=17, column = 4)
    PI_lbl17f = tk.Label(vs_frame,text="Swtch4RR3Main_HMIb fdbck",justify="center",width=20, borderwidth=1, relief="solid")
    PI_lbl17f.grid(row=17, column =5)
    PI_lbl17g = tk.Button(vs_frame,text=UpdatePISwitch1,pady=0,justify="center",width=8,borderwidth=1,bg="lightgrey",relief="raised",
                         command=lambda:UpdateSwitchFdBck(1,PIIndex59.get(),1))
    PI_lbl17g.grid(row=17, column = 6)
    PI_btn17h = tk.Label(vs_frame,text=HMI_PB,justify="center",width=10, borderwidth=1, relief="solid")
    PI_btn17h.grid(row=17, column = 7)

    PI_lbl18e = tk.Label(vs_frame,textvariable=PIIndex61,justify="center",width=6, borderwidth=3,relief="solid")
    PI_lbl18e.grid(row=18, column = 4)
    PI_lbl18f = tk.Label(vs_frame,text="Swtch5Main_HMIb fdbck",justify="center",width=20, borderwidth=1, relief="solid")
    PI_lbl18f.grid(row=18, column =5)
    PI_lbl18g = tk.Button(vs_frame,text=UpdatePISwitch1,pady=0,justify="center",width=8,borderwidth=1,bg="lightgrey",relief="raised",
                         command=lambda:UpdateSwitchFdBck(1,PIIndex61.get(),1)) 
    PI_lbl18g.grid(row=18, column = 6)
    PI_btn18h = tk.Label(vs_frame,text=HMI_PB,justify="center",width=10, borderwidth=1, relief="solid")
    PI_btn18h.grid(row=18, column = 7)

    PI_lbl19e = tk.Label(vs_frame,textvariable=PIIndex63,justify="center",width=6, borderwidth=3,relief="solid")
    PI_lbl19e.grid(row=19, column = 4)
    PI_lbl19f = tk.Label(vs_frame,text="Swtch6RRMain_HMIb fdbck",justify="center",width=20, borderwidth=1, relief="solid")
    PI_lbl19f.grid(row=19, column =5)
    PI_lbl19g = tk.Button(vs_frame,text=UpdatePISwitch1,justify="center",pady=0,width=8,borderwidth=1,bg="lightgrey",relief="raised",
                         command=lambda:UpdateSwitchFdBck(1,PIIndex63.get(),1)) 
    PI_lbl19g.grid(row=19, column = 6)
    PI_btn19h = tk.Label(vs_frame,text=HMI_PB,justify="center",width=10, borderwidth=1, relief="solid")
    PI_btn19h.grid(row=19, column = 7)

    PI_lbl20e = tk.Label(vs_frame,textvariable=PIIndex64,justify="center",width=6, borderwidth=3,relief="solid")
    PI_lbl20e.grid(row=20, column = 4)
    PI_lbl20f = tk.Label(vs_frame,text="HMI_TramQuietb",justify="center",width=20, borderwidth=1, relief="solid")
    PI_lbl20f.grid(row=20, column =5)
    PI_ent20g = tk.Button(vs_frame, text="--",width=8,borderwidth=1,bg="lightgrey",
                        relief="raised",pady=0) 
    PI_ent20g.grid(row=20, column = 6)
    PI_lbl20h = tk.Label(vs_frame,textvariable=HMI_PB,justify="center",width=10, borderwidth=1, relief="solid")
    PI_lbl20h.grid(row=20, column = 7)

    PI_lbl21e = tk.Label(vs_frame,textvariable=PIIndex65,justify="center",width=6, borderwidth=3,relief="solid",pady=0, padx=0)
    PI_lbl21e.grid(row=21, column = 4,padx=0) #  feedback to HMI
    PI_lbl21f = tk.Label(vs_frame,text="TramStn1_HMIb fdbck",justify="center",width=20, borderwidth=1, relief="solid",pady=0, padx=0)
    PI_lbl21f.grid(row=21, column =5,padx=0)
    PI_lbl21g = tk.Button(vs_frame,text="@Stn?",justify="center",
                          width=10, bg="yellow",borderwidth=1, relief="solid",pady=0, padx=0,
                          command=lambda:HMI_Interface(0,PIIndex65.get(),2))
    PI_lbl21g.configure(command=lambda:HMI_PB(0,PIIndex65.get(),2))
    PI_lbl21g.grid(row=21, column = 6,padx=0)
    PI_lbl21h = tk.Label(vs_frame,text=HMI_Interface,justify="center",width=10, borderwidth=1, relief="solid",pady=0, padx=0)
    PI_lbl21h.grid(row=21, column = 7,padx=0)

    PI_lbl22e = tk.Label(vs_frame,textvariable=PIIndex66,justify="center",width=6, borderwidth=3,relief="solid")
    PI_lbl22e.grid(row=22, column = 4)
    PI_lbl22f = tk.Label(vs_frame,text="TramStn2_HMIb feedback",justify="center",width=20, borderwidth=1, relief="solid")
    PI_lbl22f.grid(row=22, column =5)
    PI_lbl22g = tk.Button(vs_frame,text="@Stn?",justify="center",
                          width=10, bg="yellow",borderwidth=1, relief="solid",pady=0,
                          command=lambda:HMI_Interface(0,PIIndex66.get(),2))
    PI_lbl22g.configure(command=lambda:HMI_PB(0,PIIndex66.get(),2))
    PI_lbl22g.grid(row=22, column = 6)
    PI_lbl22h = tk.Label(vs_frame,text=HMI_Interface,justify="center",width=10, borderwidth=1, relief="solid")
    PI_lbl22h.grid(row=22, column = 7)

    PI_lbl23e = tk.Label(vs_frame,textvariable=PIIndex67,justify="center",width=6, borderwidth=3,relief="solid")
    PI_lbl23e.grid(row=23, column = 4)
    PI_lbl23f = tk.Label(vs_frame,text="TramStn3_HMIb feedback",justify="center",width=20, borderwidth=1, relief="solid")
    PI_lbl23f.grid(row=23, column =5)
    PI_lbl23g = tk.Button(vs_frame,text="@Stn?",justify="center",pady=0,
                          width=10, bg="yellow",borderwidth=1, relief="solid",
                          command=lambda:HMI_Interface(0,PIIndex67.get(),2))
    PI_lbl23g.configure(command=lambda:HMI_PB(0,PIIndex67.get(),2))
    PI_lbl23g.grid(row=23, column = 6)
    PI_lbl23h = tk.Label(vs_frame,text=HMI_Interface,justify="center",width=10, borderwidth=1, relief="solid")
    PI_lbl23h.grid(row=23, column = 7)

    PI_lbl24e = tk.Label(vs_frame,textvariable=PIIndex68,justify="center",width=6, borderwidth=3,relief="solid")
    PI_lbl24e.grid(row=24, column = 4)
    PI_lbl24f = tk.Label(vs_frame,text="TramStn4_HMIb feedback",justify="center",width=20, borderwidth=1, relief="solid")
    PI_lbl24f.grid(row=24, column =5)
    PI_lbl24g = tk.Button(vs_frame,text="@Stn?",justify="center",pady=0,
                          width=10, bg="yellow",borderwidth=1, relief="solid",
                          command=lambda:HMI_Interface(0,PIIndex68.get(),2))
    PI_lbl24g.configure(command=lambda:HMI_PB(0,PIIndex68.get(),2))
    PI_lbl24g.grid(row=24, column = 6)
    PI_lbl24h = tk.Label(vs_frame,text=HMI_PB,justify="center",width=10, borderwidth=1, relief="solid")
    PI_lbl24h.grid(row=24, column = 7)

    PI_lbl25e = tk.Label(vs_frame,textvariable=PIIndex69,justify="center",width=6, borderwidth=3,relief="solid")
    PI_lbl25e.grid(row=25, column = 4)
    PI_lbl25f = tk.Label(vs_frame,text="TramStn5_HMIb feedback",justify="center",width=20, borderwidth=1, relief="solid")
    PI_lbl25f.grid(row=25, column =5)
    PI_lbl25g = tk.Button(vs_frame,text="@Stn?",justify="center",pady=0,
                          width=10, bg="yellow",borderwidth=1, relief="solid",
                          command=lambda:HMI_Interface(0,PIIndex69.get(),2))
    PI_lbl25g.configure(command=lambda:HMI_PB(0,PIIndex69.get(),2))     
    PI_lbl25g.grid(row=25, column = 6)
    PI_lbl25h = tk.Label(vs_frame,text=HMI_PB,justify="center",width=10, borderwidth=1, relief="solid")
    PI_lbl25h.grid(row=25, column = 7)

    PI_lbl26e = tk.Label(vs_frame,textvariable=PIIndex70,justify="center",width=6, borderwidth=3,relief="solid")
    PI_lbl26e.grid(row=26, column = 4)
    PI_lbl26f = tk.Label(vs_frame,text="TramStn6_HMIb feedback",justify="center",width=20, borderwidth=1, relief="solid")
    PI_lbl26f.grid(row=26, column =5)
    PI_lbl26g = tk.Button(vs_frame,text="@Stn?",justify="center",pady=0,
                          width=10, bg="yellow",borderwidth=1, relief="solid",
                          command=lambda:HMI_Interface(0,PIIndex70.get(),2))
    PI_lbl26g.configure(command=lambda:HMI_PB(0,PIIndex70.get(),2))
    PI_lbl26g.grid(row=26, column = 6)
    PI_lbl26h = tk.Label(vs_frame,text=HMI_PB,justify="center",width=10, borderwidth=1, relief="solid")
    PI_lbl26h.grid(row=26, column=7)

    Print_HMI = tk.Button(vs_frame,text="Print HMI db",justify="center",width=8,pady=0,borderwidth=1,bg="springgreen",
                          relief="raised",command=lambda:Print("HMI"))
    Print_HMI.grid(row=3, column=8)
    Print_PI = tk.Button(vs_frame,text="Print PI db",justify="center",width=8,pady=0,borderwidth=1,bg="springgreen",
                          relief="raised",command=lambda:Print("PI"))
    Print_PI.grid(row=4, column=8)
    Print_ALL = tk.Button(vs_frame,text="Print ALL db",justify="center",width=8,pady=0,borderwidth=1,bg="springgreen",
                          relief="raised",command=lambda:Print("ALL"))
    Print_ALL.grid(row=5, column=8)
    Print_Server = tk.Button(vs_frame,text="Prnt Server db",justify="center",width=8,pady=0,borderwidth=1,bg="goldenrod",
                          relief="raised",command=lambda:Print("Server"))
    Print_Server.grid(row=6, column=8)
    UpdateServerlbl = tk.Label(vs_frame,text="Update Server every (sec)",justify="center",width=28,pady=0,borderwidth=1,bg="springgreen",
                          relief="raised",)
    UpdateServerlbl.grid(row=7, column=8)
    UpdateServerspin=tk.Spinbox(vs_frame, from_=0.100,to=2.00,increment=0.5,textvariable=var1,
                            justify="center",width=18,format="%.03f",font=('Times new roman',18,'bold'))
    UpdateServerspin.grid(row=8, column=8) 

    Terminallbl=tk.Label(vs_frame,text="TERMINAL",borderwidth=1,relief="solid",justify="center",width=30, font=('Times new roman',12,'bold'),bg="lightgrey")
    Terminallbl.grid(row=20, column=8,columnspan=2)
    Terminal = tk.Label(vs_frame,textvariable=terminal,justify="left",width=35,height=2,padx=0,pady=0,borderwidth=1,bg="aqua",font=('Times new roman',10,'bold'))
    #Terminallbl.grid(row=21, column=8,columnspan=2,rowspan=2)
    Terminal.grid(row=21,column=8,columnspan=2,rowspan=2)

    if firstpass:
        HMI03newb, HMI03oldb = False, True
        receive_thread = threading.Thread(target=receive,daemon=True)
        receive_thread.start()
        time.sleep(0.100)
        handlepaul_thread = threading.Thread(target=handlepaul,daemon=True)
        handlepaul_thread.start()
        # Load initial values from DB
        for i in range(81):
            if i > 2 and i <11:
                temp = GUIdb.get(query['INDEX'] == i)
                temp1 = temp.get("HMI_VALUEb")
                if temp1 == 1: temp1 = "True"
                else: temp1 = "False"
            elif i >= 11 and i <= 23:
                temp = GUIdb.get(query['INDEX'] == i)
                temp1 = temp.get("PI_VALUEb")
                if temp1 == 1: temp1,back = "True","lawngreen"
                else: temp1,back = "False", "salmon"           
            match i:
                case 1:
                    temp = GUIdb.get(query['INDEX'] == i)
                    temp1 = temp.get("HMI_VALUEi")
                    PI_lbl4h.configure(text=temp1)
                case 2:
                    temp = GUIdb.get(query['INDEX'] == i)
                    temp1 = temp.get("HMI_VALUEi")
                    PI_lbl5h.configure(text=temp1)
                case 3: PI_lbl6h.configure(text=temp1)
                case 4: PI_lbl7h.configure(text=temp1)
                case 5: PI_lbl8h.configure(text=temp1)
                case 6: PI_lbl9h.configure(text=temp1)
                case 7: PI_lbl10h.configure(text=temp1)
                case 8: 
                    if temp1: PI_lbl11h.configure(text="horn")
                    else: PI_lbl11h.configure(text=" -- ")
                case 9:                     
                    if temp1: PI_lbl12h.configure(text="RR quiet")
                    else: PI_lbl12h.configure(text="RR sound")
                case 10:                     
                    if temp1: PI_lbl13h.configure(text="whistle")
                    else: PI_lbl13h.configure(text=" -- ")  # whistle
                # SWITCHES
                case 11: #sw1
                    if temp1:
                        PI_btn14g.configure(text="RR1<>RR2",bg="lawngreen")
                        PI_lbl14h.configure(text="not cnnected",bg="lawngreen")
                    else:
                        PI_btn14g.configure(text="RR1=RR2",bg="salmon")
                        PI_lbl14h.configure(text="connected",bg="lawngreen")
                case 12: #sw2
                    if temp1:
                        PI_btn15g.configure(text="RR2<>RR3",bg="lawngreen")
                        PI_lbl15h.configure(text="not cnnected", bg="lawngreen")
                    else:
                        PI_btn15g.configure(text="RR2=RR3",bg="salmon")
                        PI_lbl15h.configure(text="connected", bg="salmon")
                case 13: # sw 3
                    if temp1:
                        PI_btn16g.configure(text="RR3<>RR4",bg="lawngreen")
                        PI_btn16h.configure(text="not cnnected", bg="lawngreen") 
                    else:
                        PI_btn16g.configure(text="RR3=RR4",bg="salmon")
                        PI_btn16h.configure(text="connected", bg="salmon")
                case 14: # sw 4
                    if temp1:
                        PI_lbl17g.configure(text="RR4<>RR5",bg="lawngreen")
                        PI_btn17h.configure(text="not cnnected",bg="lawngreen") 
                    else:
                        PI_lbl17g.configure(text="RR4=RR5",bg="salmon")
                        PI_btn17h.configure(text="connected",bg="salmon")
                case 15: # sw 5
                    if temp1:
                        PI_lbl18g.configure(text="RR5<>RR6",bg="lawngreen")
                        PI_btn18h.configure(text="not cnnected",bg="lawngreen")  
                    else:
                        PI_lbl18g.configure(text="RR5=RR6",bg="salmon")
                        PI_btn18h.configure(text="connected",bg="salmon")
                case 16: # sw 6
                    if temp1:
                        PI_lbl19g.configure(text="RR6<>RR7",bg="lawngreen")
                        PI_btn19h.configure(text="not cnncted",bg="lawngreen")
                    else:
                        PI_lbl19g.configure(text="RR6=RR7",bg="salmon")
                        PI_btn19h.configure(text="connected",bg="salmon")
                case 17: # HMI_TramQuietb
                    if temp1:HMI_lbl20d.configure(text="quiet")
                    else:HMI_lbl20d.configure(text="sound")
                    PI_lbl20h.configure(text=temp1) 
                # Tram Stations
                case 18: # TramStn1_HMIb fdbck
                    if temp1:
                        HMI_lbl21d.configure(text="@ STN",bg=back)
                        PI_lbl21h.configure(text="not @ STN",bg=back)
                    else:
                        HMI_lbl21d.configure(text="@ STN",bg=back) 
                        PI_lbl21h.configure(text="not @ STN",bg=back) 
                case 19: # TramStn2_HMIb fdbck
                    temp2a = GUIdb.get(query['INDEX'] == i)
                    temp2b = temp.get("PI_VALUEb")
                    if temp2b: HMI_lbl22d.configure(text="bypass",bg=back)
                    else: HMI_lbl22d.configure(text="stop",bg=back)
                    if temp1: PI_lbl22h.configure(text="@ STN",bg=back) 
                    else: PI_lbl22h.configure(text="not @ STN",bg=back)
                case 20: # TramStn3_HMIb fdbck
                    temp2a = GUIdb.get(query['INDEX'] == i)
                    temp2b = temp.get("PI_VALUEb")
                    if temp2b: HMI_lbl23d.configure(text="bypass",bg=back)
                    else: HMI_lbl23d.configure(text="stop",bg=back)
                    if temp1: PI_lbl23h.configure(text="@ STN",bg=back) 
                    else: PI_lbl23h.configure(text="not @ STN",bg=back)
                case 21: # TramStn4_HMIb fdbck
                    if temp1: 
                        HMI_lbl24d.configure(text="@ STN",bg=back)
                        PI_lbl24h.configure(text="@ STN",bg=back)
                    else: 
                        HMI_lbl24d.configure(text="@ STN",bg=back)
                        PI_lbl24h.configure(text="not @ STN",bg=back) 
                case 22: # TramStn5_HMIb fdbck
                    temp2a = GUIdb.get(query['INDEX'] == i)
                    temp2b = temp.get("PI_VALUEb")
                    if temp2b: HMI_lbl25d.configure(text="bypass",bg=back)
                    else: HMI_lbl25d.configure(text="stop",bg=back)
                    if temp1: PI_lbl25h.configure(text="@ STN",bg=back)
                    else: PI_lbl25h.configure(text="not @ STN",bg=back) 
                case 23: # TramStn6_HMIb fdbck
                    temp2a = GUIdb.get(query['INDEX'] == i)
                    temp2b = temp.get("PI_VALUEb")
                    if temp2b: HMI_lbl26d.configure(text="bypass",bg=back)
                    else: HMI_lbl26d.configure(text="stop",bg=back)
                    if temp1: PI_lbl26h.configure(text="@ STN",bg=back)
                    else: PI_lbl26h.configure(text="not @ STN",bg=back) 
        firstpass = False

    UpdateSpeed1a()
    UpdateSpeed1c()
    UpdateSpeed2a()
    UpdateHMIRHT()
    UpdateHMI_TramStopTime()
    UpdatePISwitch1()
    Time()
    root.mainloop()