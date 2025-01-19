import socket
import time
from time import sleep
import serial
import gpiozero
from serial.tools import list_ports as list_ports
import random
import pygame
import os
from pygame.locals import *
import json
import threading
from json import dumps as json_dumps, loads as json_loads
from tinydb import TinyDB, Query
from tinydb.storages import JSONStorage
from tinydb.middlewares import CachingMiddleware
from tinydb_smartcache  import *
from tinydb_smartcache import SmartCacheTable
from tinydb.storages import MemoryStorage

#Define TInyDB
query = Query()  # tinydb query object
firstb = False
FORMAT = "utf-8"
# Nickname
NICKNAME = "PI" # for server

PIdb = TinyDB(storage=MemoryStorage) # Name of DataBase

Connectionb = False
for i in range(20):
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client.connect(('127.0.0.1', 55555))
        Connectionb = True
        break
    except:
        print("\nSTART SERVER!, CHECK every 1 sec for ", 20-i, " sec")
        time.sleep(1.000)

def LoadDB():
    PIdb.insert({"INDEX": 1, "TAG":"HMI_RHT", "HMI_VALUEi": 25, "HMI_VALUEb": False, "PI_VALUEf": 0.0, "PI_VALUEb": True, "HMI_READi": 0})
    PIdb.insert({"INDEX": 2, "TAG":"HMI_TramStopTime", "HMI_VALUEi": 10,"HMI_VALUEb":True, "PI_VALUEf": 0.0, "PI_VALUEb": True, "HMI_READi": 0})
    PIdb.insert({"INDEX": 3, "TAG":"HMI_AllQuietb", "HMI_VALUEi": 0, "HMI_VALUEb": False, "PI_VALUEf": 0.0, "PI_VALUEb": True, "HMI_READi": 0})
    PIdb.insert({"INDEX": 4, "TAG":"HMI_LIGHTONOFFb", "HMI_VALUEi": 0, "HMI_VALUEb": True, "PI_VALUEf": 0.0, "PI_VALUEb": True, "HMI_READi": 0})
    PIdb.insert({"INDEX": 5, "TAG":"HMI_RR2_RR3Pwrb", "HMI_VALUEi": 0, "HMI_VALUEb": False, "PI_VALUEf": 0.0, "PI_VALUEb": True, "HMI_READi": 0})
    PIdb.insert({"INDEX": 6, "TAG":"HMI_RRBellb", "HMI_VALUEi": 0, "HMI_VALUEb": True, "PI_VALUEf": 0.0, "PI_VALUEb": True, "HMI_READi": 0})
    PIdb.insert({"INDEX": 7, "TAG":"HMI_RRDieselSteamb", "HMI_VALUEi": 0, "HMI_VALUEb": False, "PI_VALUEf": 0.0, "PI_VALUEb": True, "HMI_READi": 0})
    PIdb.insert({"INDEX": 8, "TAG":"HMI_RRHornb", "HMI_VALUEi": 0, "HMI_VALUEb": True, "PI_VALUEf": 0.0, "PI_VALUEb": True, "HMI_READi": 0})
    PIdb.insert({"INDEX": 9, "TAG":"HMI_RRQuietb", "HMI_VALUEi": 0, "HMI_VALUEb": False, "PI_VALUEf": 0.0, "PI_VALUEb": True, "HMI_READi": 0})
    PIdb.insert({"INDEX": 10, "TAG":"HMI_RRWhistleb", "HMI_VALUEi": 0, "HMI_VALUEb": True, "PI_VALUEf": 0.0, "PI_VALUEb": True, "HMI_READi": 0})
    PIdb.insert({"INDEX": 11, "TAG":"HMI_Switch1ABb", "HMI_VALUEi": 0, "HMI_VALUEb": True, "PI_VALUEf": 0.0, "PI_VALUEb": True, "HMI_READi": 0})
    PIdb.insert({"INDEX": 12, "TAG":"HMI_Switch2RR3b", "HMI_VALUEi": 0, "HMI_VALUEb":True, "PI_VALUEf": 0.0, "PI_VALUEb": True, "HMI_READi": 0})
    PIdb.insert({"INDEX": 13, "TAG":"HMI_Switch3RR4b", "HMI_VALUEi": 0, "HMI_VALUEb": False, "PI_VALUEf": 0.0, "PI_VALUEb":True, "HMI_READi": 0})
    PIdb.insert({"INDEX": 14, "TAG":"HMI_Switch4RR3b", "HMI_VALUEi": 0, "HMI_VALUEb": True, "PI_VALUEf": 0.0, "PI_VALUEb": True, "HMI_READi": 0})
    PIdb.insert({"INDEX": 15, "TAG":"HMI_Switch5ABb", "HMI_VALUEi": 0, "HMI_VALUEb": False, "PI_VALUEf": 0.0, "PI_VALUEb": True, "HMI_READi": 0})
    PIdb.insert({"INDEX": 16, "TAG":"HMI_Switch6ABb", "HMI_VALUEi": 0, "HMI_VALUEb": True, "PI_VALUEf": 0.0, "PI_VALUEb": True, "HMI_READi": 0})
    PIdb.insert({"INDEX": 17, "TAG":"HMI_TramQuietb", "HMI_VALUEi": 0, "HMI_VALUEb": False, "PI_VALUEf": 0.0, "PI_VALUEb": True, "HMI_READi": 0})
    PIdb.insert({"INDEX": 18, "TAG":"HMI_TramStpStn_2b", "HMI_VALUEi":0, "HMI_VALUEb": False, "PI_VALUEf": 0.0, "PI_VALUEb":True, "HMI_READi": 0})
    PIdb.insert({"INDEX": 19, "TAG":"HMI_TramStpStn_3b", "HMI_VALUEi": 0, "HMI_VALUEb": False, "PI_VALUEf": 0.0, "PI_VALUEb": True, "HMI_READi": 0})
    PIdb.insert({"INDEX": 20, "TAG":"HMI_TramStpStn_5b", "HMI_VALUEi":0, "HMI_VALUEb": False, "PI_VALUEf": 0.0, "PI_VALUEb":True, "HMI_READi": 0})
    PIdb.insert({"INDEX": 21, "TAG":"HMI_TramStpStn_6b", "HMI_VALUEi": 0, "HMI_VALUEb": False, "PI_VALUEf": 0.0, "PI_VALUEb": True, "HMI_READi": 0})
    PIdb.insert({"INDEX": 22, "TAG":"HMI_Future_1", "HMI_VALUEi": 0, "HMI_VALUEb": True, "PI_VALUEf": 0.0, "PI_VALUEb": True, "HMI_READi": 0})
    PIdb.insert({"INDEX": 23, "TAG":"HMI_Future_2", "HMI_VALUEi": 0, "HMI_VALUEb": True, "PI_VALUEf": 0.0, "PI_VALUEb": True, "HMI_READi": 0})
    PIdb.insert({"INDEX": 24, "TAG":"HMI_Future_3", "HMI_VALUEi": 0, "HMI_VALUEb": True, "PI_VALUEf": 0.0, "PI_VALUEb": True, "HMI_READi": 0})
    PIdb.insert({"INDEX": 25, "TAG":"HMI_Future_4", "HMI_VALUEi": 0, "HMI_VALUEb": True, "PI_VALUEf": 0.0, "PI_VALUEb": True, "HMI_READi": 0})
    PIdb.insert({"INDEX": 26, "TAG":"HMI_Future_5", "HMI_VALUEi": 0, "HMI_VALUEb": True, "PI_VALUEf": 0.0, "PI_VALUEb": True, "HMI_READi": 0})
    PIdb.insert({"INDEX": 27, "TAG":"HMI_Future_6", "HMI_VALUEi": 0, "HMI_VALUEb": True, "PI_VALUEf": 0.0, "PI_VALUEb": True, "HMI_READi": 0})
    PIdb.insert({"INDEX": 28, "TAG":"HMI_Future_7", "HMI_VALUEi": 0, "HMI_VALUEb": True, "PI_VALUEf": 0.0, "PI_VALUEb": True, "HMI_READi": 0})
    PIdb.insert({"INDEX": 29, "TAG":"HMI_Future_8", "HMI_VALUEi": 0, "HMI_VALUEb": True, "PI_VALUEf": 0.0, "PI_VALUEb": True, "HMI_READi": 0})
    PIdb.insert({"INDEX": 30, "TAG":"HMI_Future_9", "HMI_VALUEi": 0, "HMI_VALUEb": True, "PI_VALUEf": 0.0, "PI_VALUEb": True, "HMI_READi": 0})
    PIdb.insert({"INDEX": 31, "TAG":"HMI_Future_10", "HMI_VALUEi": 0, "HMI_VALUEb": True, "PI_VALUEf": 0.0, "PI_VALUEb": True, "HMI_READi": 0})
    PIdb.insert({"INDEX": 32, "TAG":"HMI_Future_11", "HMI_VALUEi": 0, "HMI_VALUEb": True, "PI_VALUEf": 0.0, "PI_VALUEb": True, "HMI_READi": 0})
    PIdb.insert({"INDEX": 33, "TAG":"HMI_Future_12", "HMI_VALUEi": 0, "HMI_VALUEb": True, "PI_VALUEf": 0.0, "PI_VALUEb": True, "HMI_READi": 0})
    PIdb.insert({"INDEX": 34, "TAG":"HMI_Future_13", "HMI_VALUEi": 0, "HMI_VALUEb": True, "PI_VALUEf": 0.0, "PI_VALUEb": True, "HMI_READi": 0})
    PIdb.insert({"INDEX": 35, "TAG":"HMI_Future_14", "HMI_VALUEi": 0, "HMI_VALUEb": True, "PI_VALUEf": 0.0, "PI_VALUEb": True, "HMI_READi": 0})
    PIdb.insert({"INDEX": 36, "TAG":"HMI_Future_15", "HMI_VALUEi": 0, "HMI_VALUEb": True, "PI_VALUEf": 0.0, "PI_VALUEb": True, "HMI_READi": 0})
    PIdb.insert({"INDEX": 37, "TAG":"HMI_Future_16", "HMI_VALUEi": 0, "HMI_VALUEb": True, "PI_VALUEf": 0.0, "PI_VALUEb": True, "HMI_READi": 0})
    PIdb.insert({"INDEX": 38, "TAG":"HMI_Future_17", "HMI_VALUEi": 0, "HMI_VALUEb": True, "PI_VALUEf": 0.0, "PI_VALUEb": True, "HMI_READi": 0})
    PIdb.insert({"INDEX": 39, "TAG":"HMI_Future_18", "HMI_VALUEi": 0, "HMI_VALUEb": True, "PI_VALUEf": 0.0, "PI_VALUEb": True, "HMI_READi": 0})
    PIdb.insert({"INDEX": 40, "TAG":"HMI_Future_19", "HMI_VALUEi": 0, "HMI_VALUEb": True, "PI_VALUEf": 0.0, "PI_VALUEb": True, "HMI_READi": 0})
    PIdb.insert({"INDEX": 41, "TAG":"HMI_Future_20", "HMI_VALUEi": 0, "HMI_VALUEb": True, "PI_VALUEf": 0.0, "PI_VALUEb": True, "HMI_READi": 0})
    PIdb.insert({"INDEX": 42, "TAG":"HMI_Future_21", "HMI_VALUEi": 0, "HMI_VALUEb": True, "PI_VALUEf": 0.0, "PI_VALUEb": True, "HMI_READi": 0})
    PIdb.insert({"INDEX": 43, "TAG":"HMI_Future_22", "HMI_VALUEi": 0, "HMI_VALUEb": True, "PI_VALUEf": 0.0, "PI_VALUEb": True, "HMI_READi": 0})
    PIdb.insert({"INDEX": 44, "TAG":"HMI_Future_23", "HMI_VALUEi": 0, "HMI_VALUEb": True, "PI_VALUEf": 0.0, "PI_VALUEb": True, "HMI_READi": 0})
    PIdb.insert({"INDEX": 45, "TAG":"HMI_Future_24", "HMI_VALUEi": 0, "HMI_VALUEb": True, "PI_VALUEf": 0.0, "PI_VALUEb": True, "HMI_READi": 0})
    PIdb.insert({"INDEX": 46, "TAG":"HMI_Future_25", "HMI_VALUEi": 0, "HMI_VALUEb": True, "PI_VALUEf": 0.0, "PI_VALUEb": True, "HMI_READi": 0})
    PIdb.insert({"INDEX": 47, "TAG":"HMI_Future_26", "HMI_VALUEi": 0, "HMI_VALUEb": True, "PI_VALUEf": 0.0, "PI_VALUEb": True, "HMI_READi": 0})
    PIdb.insert({"INDEX": 48, "TAG":"HMI_Future_27", "HMI_VALUEi": 0, "HMI_VALUEb": True, "PI_VALUEf": 0.0, "PI_VALUEb": True, "HMI_READi": 0})
    PIdb.insert({"INDEX": 49, "TAG":"HMI_Future_28", "HMI_VALUEi": 0, "HMI_VALUEb": True, "PI_VALUEf": 0.0, "PI_VALUEb":True, "HMI_READi": 0})
    PIdb.insert({"INDEX": 50, "TAG":"RR1ABspeed_HMI", "HMI_VALUEi": 0, "HMI_VALUEb": True, "PI_VALUEf": 0.12, "PI_VALUEb": True, "HMI_READi": 0})
    PIdb.insert({"INDEX": 51, "TAG":"RR1CDspeed_HMI", "HMI_VALUEi": 0, "HMI_VALUEb": True, "PI_VALUEf": 0.12, "PI_VALUEb": True, "HMI_READi": 0})
    PIdb.insert({"INDEX": 52, "TAG":"RR2ABspeed_HMI", "HMI_VALUEi": 0, "HMI_VALUEb": True, "PI_VALUEf": 0.12, "PI_VALUEb": True, "HMI_READi": 0})
    PIdb.insert({"INDEX": 53, "TAG":"Switch1Main_HMIb", "HMI_VALUEi": 0, "HMI_VALUEb": True, "PI_VALUEf": 0.12, "PI_VALUEb": True, "HMI_READi": 0})
    PIdb.insert({"INDEX": 54, "TAG":"open", "HMI_VALUEi": 0, "HMI_VALUEb": True, "PI_VALUEf": 0.12, "PI_VALUEb": True, "HMI_READi": 0})
    PIdb.insert({"INDEX": 55, "TAG":"Switch2RR3Main_HMIb", "HMI_VALUEi": 0, "HMI_VALUEb": True, "PI_VALUEf": 0.12, "PI_VALUEb": True, "HMI_READi": 0})
    PIdb.insert({"INDEX": 56, "TAG":"open", "HMI_VALUEi": 0, "HMI_VALUEb": True, "PI_VALUEf": 0.12, "PI_VALUEb": True, "HMI_READi": 0})
    PIdb.insert({"INDEX": 57, "TAG":"Switch3RR4Main_HMIb", "HMI_VALUEiy": 0, "HMI_VALUEb": True, "PI_VALUEf": 0.12, "PI_VALUEb": True, "HMI_READi": 0})
    PIdb.insert({"INDEX": 58, "TAG":"open", "HMI_VALUEi": 0, "HMI_VALUEb": True, "PI_VALUEf": 0.12, "PI_VALUEb": True, "HMI_READi": 0})
    PIdb.insert({"INDEX": 59, "TAG":"Switch4RR3Main_HMIb", "HMI_VALUEi": 0, "HMI_VALUEb": True, "PI_VALUEf": 0.12, "PI_VALUEb": True, "HMI_READi": 0})
    PIdb.insert({"INDEX": 60, "TAG":"open", "HMI_VALUEi": 0, "HMI_VALUEb": True, "PI_VALUEf": 0.12, "PI_VALUEb": True, "HMI_READi": 0})
    PIdb.insert({"INDEX": 61, "TAG":"Switch5Main_HMIb", "HMI_VALUEi": 0, "HMI_VALUEb": True, "PI_VALUEf": 0.12, "PI_VALUEb": True, "HMI_READi": 0 })
    PIdb.insert({"INDEX": 62, "TAG":"open", "HMI_VALUEi": 0, "HMI_VALUEb": True, "PI_VALUEf": 0.12, "PI_VALUEb": True, "HMI_READi": 0})
    PIdb.insert({"INDEX": 63, "TAG":"Switch6Main_HMIb", "HMI_VALUEi": 0, "HMI_VALUEb": True, "PI_VALUEf": 0.12, "PI_VALUEb": True, "HMI_READi": 0})
    PIdb.insert({"INDEX": 64, "TAG":"RR2orRR3Pwr_HMIb", "HMI_VALUEi": 0, "HMI_VALUEb": True, "PI_VALUEf": 0.12, "PI_VALUEb": False, "HMI_READi": 0})
    PIdb.insert({"INDEX": 65, "TAG":"TramStn1_HMIb", "HMI_VALUEi": 0, "HMI_VALUEb":False, "PI_VALUEf": 0.12, "PI_VALUEb": False, "HMI_READi": 0})
    PIdb.insert({"INDEX": 66, "TAG":"TramStn2_HMIb", "HMI_VALUEi": 0, "HMI_VALUEb": False, "PI_VALUEf": 0.12, "PI_VALUEb": False, "HMI_READi": 0})
    PIdb.insert({"INDEX": 67, "TAG":"TramStn3_HMIb", "HMI_VALUEi": 0, "HMI_VALUEb": False, "PI_VALUEf": 0.12, "PI_VALUEb": False, "HMI_READi": 0})
    PIdb.insert({"INDEX": 68, "TAG":"TramStn4_HMIb", "HMI_VALUEi": 0, "HMI_VALUEb": False, "PI_VALUEf": 0.12, "PI_VALUEb": True, "HMI_READi": 0})
    PIdb.insert({"INDEX": 69, "TAG":"TramStn5_HMIb", "HMI_VALUEi": 0, "HMI_VALUEb": False, "PI_VALUEf": 0.12, "PI_VALUEb": False, "HMI_READi": 0})
    PIdb.insert({"INDEX": 70, "TAG":"TramStn6_HMIb", "HMI_VALUEi": 0, "HMI_VALUEb": False, "PI_VALUEf": 0.12, "PI_VALUEb": False, "HMI_READi": 0})
    PIdb.insert({"INDEX": 71, "TAG":"PI_Future_1", "HMI_VALUEi": 0, "HMI_VALUEb": True, "PI_VALUEf": 0.12, "PI_VALUEb": False, "HMI_READi": 0})
    PIdb.insert({"INDEX": 72, "TAG":"PI_Future_2", "HMI_VALUEi": 0, "HMI_VALUEb": True, "PI_VALUEf": 0.12, "PI_VALUEb": False, "HMI_READi": 0})
    PIdb.insert({"INDEX": 73, "TAG":"PI_Future_3", "HMI_VALUEi": 0, "HMI_VALUEb": True, "PI_VALUEf": 0.12, "PI_VALUEb": False, "HMI_READi": 0})
    PIdb.insert({"INDEX": 74, "TAG":"PI_Future_4", "HMI_VALUEi": 0, "HMI_VALUEb": True, "PI_VALUEf": 0.12, "PI_VALUEb": False, "HMI_READi": 0})
    PIdb.insert({"INDEX": 75, "TAG":"PI_Future_5", "HMI_VALUEi": 0, "HMI_VALUEb": True, "PI_VALUEf": 0.12, "PI_VALUEb": False, "HMI_READi": 0})
    PIdb.insert({"INDEX": 76, "TAG":"PI_Future_6", "HMI_VALUEi": 0, "HMI_VALUEb": True, "PI_VALUEf": 0.12, "PI_VALUEb": False, "HMI_READi": 0})
    PIdb.insert({"INDEX": 77, "TAG":"PI_Future_6", "HMI_VALUEi": 0, "HMI_VALUEb": True, "PI_VALUEf": 0.12, "PI_VALUEb": False, "HMI_READi": 0})
    PIdb.insert({"INDEX": 78, "TAG":"PI_Future_8", "HMI_VALUEi": 0, "HMI_VALUEb": True, "PI_VALUEf": 0.12, "PI_VALUEb": False, "HMI_READi": 0})
    PIdb.insert({"INDEX": 79, "TAG":"PI_Future_9", "HMI_VALUEi": 0, "HMI_VALUEb": True, "PI_VALUEf": 0.12, "PI_VALUEb": False, "HMI_READi": 0})
    PIdb.insert({"INDEX": 80, "TAG":"PI_Future_10", "HMI_VALUEi": 0, "HMI_VALUEb": True, "PI_VALUEf": 0.12, "PI_VALUEb": False, "HMI_READi": 0})

def receive():
    """ Receive data from server and send nickname.  
    This function will continually listen for incoming data from the server. If the
    server requests a nickname, this function will send the nickname. If the server
    sends any other data, this function will store it in the 'svrmsg' variable.
    If this function encounters an error while trying to receive data, it will print
    an error message and wait 1 second before trying again. If the error persists for
    20 seconds, this function will stop running. """
    global ServersendingUpdatesb, ServertoSendb, svrmsg, client
    print("receive started")
    while True:
        sleep(0.010) # free cpu time
        try:
            # Receive Message From Server   If 'NICK' Send Nickname
            svrmsg = client.recv(12288).decode(FORMAT)
            if svrmsg == 'NICK':
                client.send(NICKNAME.encode(FORMAT))
                time.sleep(0.100)
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

# $$$$$$$$$$$$$$ HANDLEPI $$$$$$$$$$$$
def handlePI():  			# Sending Messages To Server
    global ServersendingUpdatesb, PIdb, svrmsg, client
    print("handlePI started")
    svrmsg = "pass"
    while True:
        sleep(0.100) # free cpu time
        #print("PI svrmsg at top: ", svrmsg)
        if svrmsg =="pass" or svrmsg == "PINo":
            message = "PINew" # send if not involved in other functions
            client.send(message.encode(FORMAT))
        #print("sent PINew")
        #while svrmsg == "PIYes" or svrmsg == "PINo":
        #    sleep(0.050)
        if svrmsg == "PIYes": # Server has PI update 
            message = "ReadytoRecv"
            client.send(message.encode(FORMAT))
            sleep(0.100)
            #if svrmsg.find("[{INDEX") < 0: # not found = -1
        # Got data, save to local db - clear bit by program, not here
        elif svrmsg.find('INDEX') >= 0: # have data from server
            print("received data 686: ", svrmsg)
            json_data = json.loads(svrmsg)
            print("json_data 181: ", json_data)
            for row in range(0,len(json_data)):
                Index = json_data[row].get("INDEX")
                HMI_Valuei = json_data[row].get("HMI_VALUEi")
                HMI_Valueb = json_data[row].get("HMI_VALUEb")
                PI_Valuef = json_data[row].get("PI_VALUEf")
                PI_Valueb = json_data[row].get("PI_VALUEb")
                HMI_Readi = json_data[row].get("HMI_READi")
                PIdb.update({"HMI_VALUEi":HMI_Valuei,"HMI_VALUEb":HMI_Valueb,"PI_VALUEf":PI_Valuef,"PI_VALUEb":PI_Valueb,"HMI_READi":HMI_Readi},query.INDEX==Index)
                print("saved data: ", svrmsg)
                time.sleep(0.100)
        elif svrmsg == "ServerSENDDone":
            print("Got ServerSENDDone")

        elif svrmsg == "PINo":
            # Done with recieve, start the send 
            if PIdb.count(query.HMI_READi == 1) > 0:
                message = "SendingUpdates"
                client.send(message.encode(FORMAT))
                sleep(0.400)
            else: # nothing to send
                message = "NoUpdates"
                client.send(message.encode(FORMAT))
                sleep(0.100)
                message = "pass"
                client.send(message.encode(FORMAT))
        elif svrmsg == "ServerReady":
            print("in server ready section")
            temp2 = PIdb.search(query.HMI_READi == 1)
            temp2 = json.dumps(temp2)
            client.send(temp2.encode(FORMAT)) # send updates
            sleep(0.400)
            client.send("ClientSENDDone".encode(FORMAT))
            PIdb.update({"HMI_READi": 0}, query.HMI_READi == 1)

if __name__ == '__main__':
    if not firstb:
        LoadDB()  # Load TinyDB & start RECEIVE for Server 
        firstb = True
    receive_thread = threading.Thread(target=receive,daemon=True) #Start Receive
    receive_thread.start()
    sleep(1.000)
    handlePI_thread = threading.Thread(target=handlePI,daemon=True) # start handlePI
    handlePI_thread.start()

    while True:
        sleep(1.000)
        #print("PIdb count in MAIN: ", PIdb.count(query.HMI_READi == 2))
        #print("Line 11: ", PIdb.search(query.INDEX == 11))
        if PIdb.count(query.HMI_READi == 2) > 0: # if any data to send
            print("updating PI db")
            temp = PIdb.search(query.HMI_READi == 2)
            for row in temp:
                index = row.get("INDEX")
                HMI_Valueb = row.get("HMI_VALUEb")
                match index:
                    case 1: print("HMI #: ", index, "HMI_RHT = ", row.get("HMI_VALUEi"))
                    case 2: print("HMI #: ", index, "HMI_TramStopTime = ", row.get("HMI_VALUEi"))
                    case 3: print("HMI #: ", index, "HMI_AllQuietb = ", row.get("HMI_VALUEb"))
                    case 4: print("HMI #: ", index, "HMI_LIGHTONOFFb = ", row.get("HMI_VALUEb"))
                    case 5: print("HMI #: ", index, "HMI_RR2_RR3Pwrb = ", row.get("HMI_VALUEb"))
                    case 6: print("HMI #: ", index, "HMI_RRBellb = ", row.get("HMI_VALUEb"))
                    case 7: print("HMI #: ", index, "HMI_RRDieselSteamb = ", row.get("HMI_VALUEb"))
                    case 8: print("HMI #: ", index, "HMI_RRHornb = ", row.get("HMI_VALUEb"))
                    case 9: print("HMI #: ", index, "HMI_RRQuietb = ", row.get("HMI_VALUEb"))
                    case 10: print("HMI #: ", index, "HMI_RRWhistleb = ", row.get("HMI_VALUEb"))
                    case 11:
                        PIdb.update({"PI_VALUEb": HMI_Valueb, "HMI_READi": 1}, query.INDEX == 53)
                        sleep(0.100)
                        PIdb.update({"HMI_READi":0}, query.INDEX == 11)
                        print("updated PIdb - 11 for 53")
                        print(PIdb.search(query.INDEX == 53))
                    case 12:
                        PIdb.update({"PI_VALUEb": row.get("HMI_VALUEb"), "HMI_READi": 1}, query.INDEX == 55)
                        PIdb.update({"HMI_READi":0}, query.INDEX == 12)
                    case 13:
                        PIdb.update({"PI_VALUEb": row.get("HMI_VALUEb"), "HMI_READi": 1}, query.INDEX == 57)
                        PIdb.update({"HMI_READi":0}, query.INDEX == 13)
                    case 14:
                        PIdb.update({"PI_VALUEb": row.get("HMI_VALUEb"), "HMI_READi": 1}, query.INDEX == 59)
                        PIdb.update({"HMI_READi":0}, query.INDEX == 14)
                    case 15:
                        PIdb.update({"PI_VALUEb": row.get("HMI_VALUEb"), "HMI_READi": 1}, query.INDEX == 61)
                        PIdb.update({"HMI_READi":0}, query.INDEX == 15)
                    case 16:
                        PIdb.update({"PI_VALUEb": row.get("HMI_VALUEb"), "HMI_READi": 1}, query.INDEX == 63)
                        PIdb.update({"HMI_READi":0}, query.INDEX == 16)
                    case 17:  print("HMI_TramQuietb = ", row.get("HMI_VALUEi"))
                    case 18:  print("HMI_TramStpStn_2b = ", row.get("HMI_VALUEb"))
                    case 19:  print("HMI_TramStpStn_3b = ", row.get("HMI_VALUEb"))
                    case 20:  print("HMI_TramStpStn_5b = ", row.get("HMI_VALUEb"))
                    case 21:  print("HMI_TramStpStn_6b = ", row.get("HMI_VALUEb"))
            sleep(0.100)
