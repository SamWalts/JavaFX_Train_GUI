'''*********************************************************************
 **********PI CONTINUOUS RUNNING PROGRAMS***************
            ADDED THE TINYDB CODE 
 *********Version 19 241118 ******************************
 ********************************************************* '''
import socket
import time
from time import sleep
import serial
import gpiozero            
from serial.tools import list_ports as list_ports
import board
import neopixel_spi as neopixel
import random
import pygame
import os
from pygame.locals import * 
import json
import threading
pygame.mixer.pre_init(44100, -16, 2, 4096)
pygame.mixer.init()
os.getcwd() 
from json import dumps as json_dumps, loads as json_loads
from tinydb import TinyDB, Query
from tinydb.storages import JSONStorage
from tinydb.middlewares import CachingMiddleware
from tinydb_smartcache  import *
from tinydb_smartcache import SmartCacheTable 
from tinydb.storages import MemoryStorage

#Define TInyDB
query = Query()  # tinydb query object

FORMAT = "utf-8"
# Nickname
NICKNAME = "PI" # for server
global ServersendingUpdatesb, ServertoSendb, PIdb, svrmsg, client
ServersendingUpdatesb, ServertoSendb = False, False
svrmsg = "" # in RECEIVE used for Server Data

PIdb = TinyDB(storage=MemoryStorage) # Name of DataBase
# ************CONSTANTS**********

# Initial value for Relay Hold Time inn ms, updated by HMI
HMI_RHT, HMI_RHT_old = 25, 100 
#   HMI INPUT REGISTERS, INITIAL VALUES. CAUTION CHANGES
HMI_Switch1ABb, Switch1Main_HMIb = True, False              	#TRUE = (M01R01), False = M01R02
#HMI_Switch1_AB_RR2_RR3 = False          #(M01R02) 
HMI_Switch2RR3b, Switch2RR3Main_HMIb = True, False #  TRUE = (M01R03) FALSE = M01R04
HMI_Switch3RR4b, Switch3RR4Main_HMIb = True, False #TRUE = ('M01R05') FALSE = M01R06
HMI_Switch4RR3b, Switch4RR3Main_HMIb = True, False # TRUE = ('M01R07') False = M01R08
HMI_Switch5ABb, Switch5Main_HMIb, okplayleaveb = True, False, False #TRUE = ('M02R09') FALSE = M02R10
HMI_Switch6ABb, Switch6Main_HMIb = True, False  # TRUE = ('M02R11') FALSE = M02R12

switches1 = bytearray()
switches2 = bytearray()

# Define HMI Tram inputs, Set and leave, Reset to skip station
# HMI_TramStpStn_1b = True       TRAM ALWAYS STOPS HERE, False = bypass
HMI_Switch5ABb, Switch5Main_HMIb, okplayleaveb = True, False, False #TRUE = ('M02R09') FALSE = M02R10 
     
Timer2runb = False  # timer for HMI updates, every 2 seconds, speed is updated
# HMI_TramStpStn_4b = True Tram always stops here, end of line
okplayarriveb, Tramarrive2_6b = False, False                 
SentTramStn1b, SentTramStn2b, SentTramStn3b, SentTramStn4b, SentTramStn5b, SentTramStn6b = False, False, False, False, False, False
TramStop = b''			#bytes blank keep

HMI_TramStopTime = 10			# Tram wait sec at each station limit to 10 to 30 sec HMI or PI
HMI_RR2_RR3Pwrb = False         # False = Power to RR3 True = power to RR2
#Speed readout to HMI from PI
RR1ABspeed_HMI, RR1CDspeed_HMI, RR2ABspeed_HMI = 0.0, 0.0, 0.0  

HMI_LIGHTONOFFb, LightOldb = False, False# TOGGLE SWITCH, same boolean input on off
# SPEED TURNS RED ON > 40MPH, PI calcs MPH and puts in this reg. floating point
RR1ABspeed_HMI, RR1CDspeed_HMI, RR2ABspeed_HMI = 0.0, 0.0, 0.0
# SAM. hmi speed alarm and alarm value totally within HMI scope
# used to get the correct port (ttyACM?)
RelayNum18, RelayNum916, SOUND, RelayNum3, TRM_LGHT = '', '', '', '', ''

RR1ABTmrb, RR1CDTmrb, RR2ABTmrb = False, False, False

#   SETUP LOCAL I/O  USING ALL GPIO NUMBERS, not physical pin number 
# Push Button inputs and logic
PButton1 = gpiozero.Button(4, pull_up=False, bounce_time=0.01, hold_time=1, hold_repeat = False) #P Pin 7
PButton2 = gpiozero.Button(17, pull_up=False, bounce_time=0.01, hold_time=1, hold_repeat = False) #P Pin 11
PButton3 = gpiozero.Button(27, pull_up=False, bounce_time=0.01, hold_time=1, hold_repeat = False) #P Pin 13
PButton4 = gpiozero.Button(22, pull_up=False, bounce_time=0.01, hold_time=1, hold_repeat = False) #P Pin 15
PButton5 = gpiozero.Button(9, pull_up=False, bounce_time=0.01, hold_time=1, hold_repeat = False) #P Pin 35
#
RR2orRR3 = gpiozero.LED(12, active_high=True, initial_value = False)
button1b, button2b, button3b, button4b, button5b = False, False, False, False, False
TramChargeTime, TramThreshold = 0.03, 0.5

# Pauvo Station
TramStop1=gpiozero.LightSensor(5,queue_len=5,charge_time_limit=TramChargeTime,threshold=TramThreshold)#P29
# James Station
TramStop2=gpiozero.LightSensor(6,queue_len=5,charge_time_limit=TramChargeTime,threshold=TramThreshold)#P31
# Katheryn Station
TramStop3=gpiozero.LightSensor(13,queue_len=5,charge_time_limit=TramChargeTime,threshold=TramThreshold)#P33  
# S & M's Baby Girl Station
TramStop4=gpiozero.LightSensor(14,queue_len=5,charge_time_limit=TramChargeTime,threshold=TramThreshold)#P8    
# William Station
TramStop5=gpiozero.LightSensor(23,queue_len=5,charge_time_limit=TramChargeTime,threshold=TramThreshold)#P16    
# Next Baby Station
TramStop6=gpiozero.LightSensor(26,queue_len=5,charge_time_limit=TramChargeTime,threshold=TramThreshold)#P37    

# Speed Triggers -- deactive = train, active = no train
SpeedChargeTime = 0.03
SpeedThreshold = 0.5
RR1Aspeed=gpiozero.LightSensor(15,queue_len=5,charge_time_limit=SpeedChargeTime,threshold=SpeedThreshold)#P10
RR1Bspeed=gpiozero.LightSensor(25,queue_len=5,charge_time_limit=SpeedChargeTime,threshold=SpeedThreshold)#P22
RR1Cspeed=gpiozero.LightSensor(10,queue_len=5,charge_time_limit=SpeedChargeTime,threshold=SpeedThreshold)#P24
RR1Dspeed=gpiozero.LightSensor(21,queue_len=5,charge_time_limit=SpeedChargeTime,threshold=SpeedThreshold)#P21
RR2Aspeed=gpiozero.LightSensor(0,queue_len=5,charge_time_limit=SpeedChargeTime,threshold=SpeedThreshold)#P27
RR2Bspeed=gpiozero.LightSensor(16,queue_len=5,charge_time_limit=SpeedChargeTime,threshold=SpeedThreshold)#P36

# Train Sounds  CAN PLAY 1 MUSIC AND UP TO 8 SOUNDS
SndPrep = pygame.mixer.Sound
     # STEAM
StmLeaving = SndPrep('SteamLeave.wav')
StmStarting = SndPrep('stm_starting.wav')
StmSlow = SndPrep('steam_slow.wav')
StmFast = SndPrep('SteamFastRun.wav')
StmWhistle = SndPrep('Whistle.wav')
StmBell = SndPrep('Bell.wav')
# Diesel
DslHorn = SndPrep('Diesel_Horn.wav')
DslStarting = SndPrep('diesel_starting.wav')
DslMsc = SndPrep('Diesel_Music.wav')
# Tram Sounds
TrmArrive = SndPrep('TramArriveDoor.wav')
TrmOpnClsDoor = SndPrep('TramDoorOpenClose.wav')
TrmLeaving = SndPrep('TramLeaveDoor.wav')

#Fun Sounds
woohoo = SndPrep('woo_hoo.wav')
clap = SndPrep('swoosh.wav')
siren1 = SndPrep('big-impact.wav')
siren2 = SndPrep('dragon-roar.wav')
siren3 = SndPrep('blaster.wav')
siren4 = SndPrep('police_siren.wav')
zapWhistle = SndPrep('zap_whistle.wav')
Laughter= SndPrep('sinister-laugh.wav')
Beep = SndPrep('game-bonus.wav')
Blast = SndPrep('fart.wav')
Beep3 = SndPrep('Beep.wav')

# Train appertanances from HMI
HMI_RRWhistleb, HMI_RRHornb, HMI_RRBellb = False, False, False

# For the LEDs cirlces around buttons
ORDER = neopixel.RGB
LEDwait = 0.005  # in seconds
LEDMulti = 40    # for rainbow module, multiplier for LED
num_LEDs = 16    # used in rainbow LEDs Buttons
PBStartLED = [0, 0, 16, 32, 48, 333]    #for circle, 1 through 4,
PBEndLED = [0, 15, 31, 47, 64, 333]

num_pixels = 72           # change if increase attached LEDs
spi = board.SPI()
#pixel_pin = board.D18
pixels = neopixel.NeoPixel_SPI(spi, num_pixels)
global LEDsCompleteb
LEDsCompleteb = True
pixels.fill(0)
Multi = 1
data = 'hello, folks'
send1x = bytearray(data, 'utf-8')
send1x.clear()
send2x = bytearray(data, 'utf-8')
send2x.clear()

# Loading word for Relay Modules
switches1.clear
switches2.clear
TrmLght = []
HMI_TramStopTimeOld = 10        #Station time hold time old
HMI_TramStopTime = 10           #Station time hold time old
Module1b = False     # boolean feedback complete with send
Module2b = False     # boolean feedback complete with send

StpRunb = False  # tram PI internal
# _____ sounds
HMI_RRDieselSteamb = False       # Initial Value for Steam Trains (TRUE = Diesel)  RR1

HMI_AllQuietb = False             # No sound from PI controlled sounds False = sound, True = True
HMI_RR1Quietb = False             # master sound for RR1 False = sound, True = True
HMI_RR2Quietb = False             # master sound for RR2 False = sound, True = True
HMI_RR3Quietb = False             # master sound for RR3 False = sound, True = True

RR1Startingb = False                # starting sound        false = no sound
RR1Stoppingb = False                # stopping sound        false = no sound
RR1SlowRunb = False                 # slow running sound    false = no sound
RR1FastRunb = False                 # Fast running sound    false = no sound

HMI_TramStpStn_2b,HMI_TramStpStn_3b,HMI_TramStpStn_5b,HMI_TramStpStn_6b = False,False,False,False
global Tram1Stopbg, Tram2Stopbg, Tram3Stopbg, Tram4Stopbg, Tram5Stopbg, Tram6Stopbg
Tram1Stopbg, Tram2Stopbg, Tram3Stopbg, Tram4Stopbg, Tram5Stopbg, Tram6Stopbg = False,False,False,False,False,False

Connectionb = False
for i in range(20):
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try: 
        client.connect(('127.0.0.1', 55555))
        Connectionb = True
        print("PI client: ", client)
        break
    except:
        print("\nSTART SERVER!, CHECK every 1 sec for ", 20-i, " sec")
        time.sleep(1.000) 

'''*****************************************************************
 ********************DEFINE FUNCTIONS*******************************
*****************************************************************'''
def SEND_MOD1(ToSend18):            # SEND TO RELAY Module 1
    global Module1b
    Module1b = False                # Trigger to main to continue
    if not(ser18.is_open):
       ser18.open
       sleep(0.01)
    try: ser18.write(ToSend18)
    except: 
        serial.SerialException
        print('SEND TO RELAY 18 FAILED')
    Module1b = True
    sleep(0.01)
    ser18.reset_output_buffer
    ToSend18=''
    return Module1b
          
def SEND_MOD2(ToSend916):               # SEND TO RELAY MOD 2
    global Module2b
    Module2b = False                    # Trigger to main to continue
    if not(ser916.is_open):             # VERIFY PORT
       ser916.open
       sleep(0.01)
       
    try: ser916.write(ToSend916)
    except: 
        serial.SerialException
        print('SEND TO RELAY 916 FAILED')
    Module2b = True
    sleep(0.01)
    ser916.reset_output_buffer
    ToSend916=''
    return Module2b

def SEND_Tram(ToSendTram):               # SEND TO TRAMSOUND pico
    print("ToSendTram: ", ToSendTram)
    if not(SerTram.is_open):             # VERIFY PORT
       SerTram.open
       sleep(0.010)
    try: SerTram.write(ToSendTram)
    except: 
        serial.SerialException
        print('SEND TO TRAM FAILED')
    sleep(0.010)
    ser916.reset_output_buffer
    ToSendTram=''
    return 

def ReadSound():				       # Read words from sound Pico
    global SndRead, SndReadRR1, SndReadRR2, SndReadRR3, SndSound2				# return sound file
         
def PiPlayTrainMusic():             # Play either Music or Sound TRAM. PAUL DELETE?
    SerSound.reset_input_buffer
    Readsnd = ''
    while SerSound.in_waiting > 0:
        Readsoundbyte = SerSound.read(9)
        Readsnd = Readsoundbyte.decode('utf-8')
    if not HMI_AllQuietb:                                # sound allowed if false
        if not HMI_RR1Quietb:
            if Readsnd == 'xxxRR1NOS': pass # No Sound from RR1
            elif Readsnd == 'xxxRR1STT':           # Starting sound
                if not HMI_RRDieselSteamb: StmSlow.play()
                else: DslStarting.play()
            elif Readsnd == 'xxxRR1STT': StmStarting.play()
            elif Readsnd == 'xxxRR1STP': StmSlow.play()
            elif Readsnd == 'xxxRR1RSW': StmSlow.play()             # Slow Run sound                      
            elif Readsnd == 'xxxRR1RFT': StmFast.play()             # Fast Run sound

            # turn off all RR1 Sounds PAUL, wait for sound to finish
            RR1Startingb = False
            RR1Stoppingb = False
            RR1SlowRunb = False
            RR1FastRunb = False 
            
            if RR1Startingb: StmLeaving.play()      # PLAY WAV FILE
            elif RR1Stoppingb: StmSlow.play()       # PLAY WAV FILE
            elif RR1SlowRunb: StmSlow.play()        # PLAY WAV FILE
            elif RR1FastRunb: StmFast.play()        # PLAY WAV FILE
        return

# * LEDs CONTROL
def NeoColorCircle(PBSelecti):       #wait = LEDwait
    global LEDsCompleteb 
    if PBSelecti == 1:
        for i1 in range(0, 16):
            pixels[i1] = (random.randint(1, 255), random.randint(1, 255), random.randint(1, 255))
            time.sleep(0.020)
            #pixels.fill(0)
    if PBSelecti == 2:        
        for i1 in range(16, 31):
            pixels[i1] = (random.randint(1, 255), random.randint(1, 255), random.randint(1, 255))
            time.sleep(0.020)
            #pixels.fill(0)
    if PBSelecti == 3:        
        for i1 in range(32, 48):
            pixels[i1] = (random.randint(1, 255), random.randint(1, 255), random.randint(1, 255))
            time.sleep(0.020)
            #pixels.fill(0)
    if PBSelecti >= 4:        
        for i1 in range(48, 64):
            pixels[i1] = (random.randint(1, 255), random.randint(1, 255), random.randint(1, 255))
            time.sleep(0.020)
            #pixels.fill(0)
    sleep(0.500)
    pixels.fill(0)
    LEDsCompleteb = True
    return LEDsCompleteb

# THE BELOW WILL FLASH EACH COLOR OF PRESSED PB AND PARTS FOR PB5
def FlashColors(PBSelecti):
    global LEDsCompleteb
    LEDwait = 0.400
          # used to prevent buffering of push button pushes
    if PBSelecti < 4:
        for i in range(PBStartLED[PBSelecti], PBEndLED[PBSelecti]):
            pixels[i]= (255, random.randint(1, 255), 0)
        sleep(LEDwait)
        for i in range(PBStartLED[PBSelecti], PBEndLED[PBSelecti]):
            pixels[i]= (0, 255, random.randint(1, 255))
        time.sleep(LEDwait)
        for i in range(PBStartLED[PBSelecti], PBEndLED[PBSelecti]):
            pixels[i]= (random.randint(1, 255), 0, 255)
        time.sleep(LEDwait)
    elif PBSelecti == 5: # do 1/2 circle on 2 LEDs, Number 2 and 4
        for i in range(16, 32, 3):
            pixels[i] = (255, 0, 0)
            pixels[i+1] = (0, 255, 0)
            pixels[i+2] = (0, 0, 255)
            time.sleep(0.010)
        for i in range(32, 48, 3):
            pixels[i] = (255, 0, 0)
            pixels[i+1] = (0, 255, 0)
            pixels[i+2] = (0, 0, 255) 
            time.sleep(0.010)
    sleep(0.300)
    pixels.fill(0)
    LEDsCompleteb = True
    return LEDsCompleteb

def TopHalf():
    global LEDsCompleteb
    wait = 0.005
    for i in range(0, 9):
        pixels[i] = (random.randint(1, 255), random.randint(1, 255), random.randint(1, 255))
        time.sleep(wait)
    for i in range(17, 24):
        pixels[i] = (random.randint(1, 255), random.randint(1, 255), random.randint(1, 255))
        time.sleep(wait)
    for i in range(33, 41):
        pixels[i] = (random.randint(1, 255), random.randint(1, 255), random.randint(1, 255))
        time.sleep(wait)
    for i in range(49, 57):
        pixels[i] = (random.randint(1, 255), random.randint(1, 255), random.randint(1, 255))
        time.sleep(wait)
    sleep(0.300)
    pixels.fill(0)
    LEDsCompleteb = True
    return LEDsCompleteb
               
#    ***************************
#   MODIFY UPON INSTALLATION: will blink 1/2 of the circle       
def BottomHalf():
    global LEDsCompleteb
    wait = 0.005
    for i in range(55, 64):
        pixels[i] = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
        time.sleep(wait)
    for i in range(17, 6, -1):
        pixels[i] = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
        time.sleep(wait)
    for i in range(32, 23, -1):
        pixels[i] = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
        time.sleep(wait)
    for i in range(47, 39, -1):
        pixels[i] = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
        time.sleep(wait)
    sleep(0.300)
    pixels.fill(0)
    LEDsCompleteb = True
    return LEDsCompleteb
            
#    ***************************
#   will blink twice
def NeoDoubleBlink():
    global LEDsCompleteb
    wait = 0.010
    for jj in range(2):
        for i2 in range(17, 33):
            pixels[i2] = (0, 150, 255)
        time.sleep(wait)
        for i2 in range(17, 33):
            pixels[i2] = (0, 255, 0)
        time.sleep(wait)
        for i2 in range(17, 33):
            pixels[i2] = (255, 0, 0)
        time.sleep(wait)
        for i2 in range(17, 33):
            pixels[i2] = (0, 0, 255)
        pixels.fill(0)
    LEDsCompleteb = True
    return LEDsCompleteb

#   Both below are the rainbow colors of the LEDs  
def wheel(pos):
    # Input a value 0 to 255 to get a color value.
    # The colours are a transition r - g - b - back to r.
    if pos < 0 or pos > 255:
        r = g = b = 0
    elif pos < 85:
        r = int(pos * 3)
        g = int(255 - pos * 3)
        b = 0
    elif pos < 170:
        pos -= 85
        r = int(255 - pos * 3)
        g = 0
        b = int(pos * 3)
    else:
        pos -= 170
        r = 0
        g = int(pos * 3)
        b = int(255 - pos * 3)
    return (r, g, b) 

def Rainbow(Multi, num_LEDs):
    global LEDsCompleteb
    for j in range(5):
        for i in range(num_LEDs): 
            pixel_index = (i * 255 // 64) + (j*Multi)
            pixels[i] = wheel(pixel_index & 255)
    sleep(0.100)
    pixels.fill(0)
    LEDsCompleteb = True
    return LEDsCompleteb
# flash all attached          

def LEDFlashAll():
    pass
    # global LEDsCompleteb
    # for i in range(64):
    #     pixels[i] = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
    # time.sleep(0.080)
    # for i in range(64):
    #     pixels[i] = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
    # time.sleep(0.080)
    # for i in range(64):
    #     pixels[i] = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
    # time.sleep(0.100)
    # LEDsCompleteb = True
    # return LEDsCompleteb

def NeoRandom(PBSelecti):
    global LEDsCompleteb
    Multi = 3
    num_LEDs = 15
    LEDsCompleteb = False        # used to prevent buffering of push button pushes
    
    x = random.randint(1, 9)
    if x == 1:
        print('neocolorcircle')         # remove all prints after confirm works
        NeoColorCircle(PBSelecti)
    elif x == 2:
        print('flashcolor')  
        FlashColors(PBSelecti)  
    elif x == 3:
        print('top half') 
        TopHalf()
    elif x == 4:
        print('bottom half')
        BottomHalf()
    elif x == 5:
        num_LEDs = 31
        Multi = 5
        print('rainbow 5')
        Rainbow(Multi, num_LEDs)        
    elif x == 6:
        print('rainbow 6')
        num_LEDs = 48
        Multi = 10
        Rainbow(Multi, num_LEDs) 
    elif x == 7:
        print('rainbow 7')
        num_LEDs = 64
        Multi = random.randint(0, 64)
        Rainbow(Multi, num_LEDs)     
    elif x == 8:
        print('LED FLASH ALL')
        LEDFlashAll()
        pixels.fill(0) # turn off LEDs
    elif x == 9:
        NeoDoubleBlink()
        pixels.fill(0) # turn off LEDs
    return LEDsCompleteb

def FromHmiPrint(Name, Value):
    print('***HMI Sent for ', Name, ' = ', Value)
                
#   TRAM STATIONS
def TramStationArrive(stationi):
    global Tram1Stopbg, Tram2Stopbg, Tram3Stopbg, Tram4Stopbg, Tram5Stopbg, Tram6Stopbg
    match stationi:
        case 1: 
            Tram1Stopbg,temp,tag,DictIndex,PiValuef,PiValueb=True, 'TRS1ON', 'TramStn1_HMIb', '65', 0.0, True
        case 2: 
            Tram2Stopbg,temp,tag,DictIndex,PiValuef,PiValueb=True, 'TRS2ON', 'TramStn2_HMIb', '66', 0.0, True
        case 3: 
            Tram3Stopbg,temp,tag,DictIndex,PiValuef,PiValueb=True, 'TRS3ON', 'TramStn3_HMIb', '67', 0.0, True
        case 4: 
            Tram4Stopbg,temp,tag,DictIndex,PiValuef,PiValueb=True, 'TRS4ON', 'TramStn4_HMIb', '68', 0.0, True
        case 5: 
            Tram5Stopbg,temp,tag,DictIndex,PiValuef,PiValueb=True, 'TRS5ON', 'TramStn5_HMIb', '69', 0.0, True
        case 6: 
            Tram6Stopbg,temp,tag,DictIndex,PiValuef,PiValueb=True, 'TRS6ON', 'TramStn6_HMIb', '70', 0.0, True
    PIdb.update({"PI_VALUEb":PiValueb, "HMI_READi": 1},query.INDEX == DictIndex)
    temp = temp.encode(FORMAT)
    SEND_Tram(temp) # Tell TRAM PICO  where Tram is
    TrmArrive.play()
    
def TramStationDepart(stationi):   
    global Tram1Stopbg, Tram2Stopbg, Tram3Stopbg, Tram4Stopbg, Tram5Stopbg, Tram6Stopbg
    match stationi:
        case 1: 
            Tram1Stopbg,temp,tag,DictIndex,PiValuef,PiValueb=False, 'TRS1OF', 'TramStn1_HMIb', '65', 0.0, False
        case 2: 
            Tram2Stopbg,temp,tag,DictIndex,PiValuef,PiValueb=False, 'TRS2OF', 'TramStn2_HMIb', '66', 0.0, False
        case 3: 
            Tram3Stopbg,temp,tag,DictIndex,PiValuef,PiValueb=False, 'TRS3OF', 'TramStn3_HMIb', '67', 0.0, False
        case 4: 
            Tram4Stopbg,temp,tag,DictIndex,PiValuef,PiValueb=False, 'TRS4OF', 'TramStn4_HMIb', '68', 0.0, False
        case 5: 
            Tram5Stopbg,temp,tag,DictIndex,PiValuef,PiValueb=False, 'TRS5OF', 'TramStn5_HMIb', '69', 0.0, False
        case 6: 
            Tram6Stopbg,temp,tag,DictIndex,PiValuef,PiValueb=False, 'TRS6OF', 'TramStn6_HMIb', '70', 0.0, False            
    PIdb.update({"PI_VALUEb":PiValueb, "HMI_READi": 1}, query.INDEX == DictIndex)
    temp = temp.encode(FORMAT)
    SEND_Tram(temp) # Tell TRAM PICO  where Tram is
    TrmLeaving.play()
    
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

#**********************************************************************************
#*******************MAIN PROGRAM***************************************************
#********************GET USB CONNECTIONS THEN LOOP TO FOLLOW***********************
if __name__ == '__main__':      #Required with multiprocessing

    HMI_Valuei = 0  # Hold HMI value
    HMI_Valueb = False  # Hold HMI value
    message = []    # holds message to send to server
    Index = 0      # index of the dictionary being querried
    DictLine = []   # Converted line from dictionary Line - LIST
    DictTemp = {}   # temp to hold a line from dictionary
    HMIValuei = 0  # Hold HMI value for PI
    HMIValueb = False  # Hold HMI value for PI
    PIValuef = 0  # Hold PI value for HMI
    PIValueb = False  # Hold PI value for HMI
    v = "HMI"

RelaysFound = False             # escape wait loop
while not RelaysFound:
    print('looking for relays')

    all_ports = list_ports.comports()
    all_port_len = len(all_ports)
    
    print('port length = ' + str(all_port_len))
    for i in range (all_port_len):
        port = all_ports[i]
        print('port = ' + str(port.device) +' = ' + str(port.description) + ', serial num = ' + str(port.serial_number))
        
    for i in range (all_port_len):
        port = all_ports[i]
        print('port = ' + str(port.description))
        if port.description == 'Relay_18 - CircuitPython CDC2 control': RelayNum18 = str(port.device)
        if port.description == 'Relay_916 - CircuitPython CDC2 control': RelayNum916 = str(port.device)
        if port.description == 'SOUND - CircuitPython CDC2 control': SOUND = str(port.device)
        if port.description == 'Relay_Mod_3 - CircuitPython CDC2 control': RelayNum3 = str(port.device)
        if port.description == 'TRM_LGHT - CircuitPython CDC2 control': TRM_LGHT = str(port.device)

    # sound Pico 
    if RelayNum18 != '' and RelayNum916 != '' and SOUND != '':
        RelaysFound = True				                    #exit while loop
        print('Found it', str(RelaysFound))
    else: sleep(3.21)                    # wait and try again forever until connected
    
    if RelayNum18 == '' or RelayNum916 == '':
        if RelayNum18 == '': print('FAILED TO MAKE CONNECTION TO 1 - 8')
        if RelayNum916 == '': print('FAILED TO MAKE CONNECTION TO 9 - 16')
        exit()      # STOP IF MISSING A RELAY CARD
    elif RelayNum18 != '' and  RelayNum916 != '':
        RelaysFound = True

    # set the Relay Module to correct ttyACM
    ser18 = serial.Serial(RelayNum18,
                            baudrate = 115200, bytesize = 8, 
                            parity = 'N', rtscts = False, dsrdtr = True, 
                            timeout = 0.1, write_timeout = 1.0, 
                            inter_byte_timeout = 0, exclusive = False)
    ser916 = serial.Serial(RelayNum916, 
                            baudrate = 115200, bytesize = 8, 
                            parity = 'N', rtscts = False, dsrdtr = True, 
                            timeout = 0.1, write_timeout = 1.0, 
                            inter_byte_timeout = 0, exclusive = False)
    SerSound = serial.Serial(SOUND, 
                            baudrate = 115200, bytesize = 8, 
                            parity = 'N', rtscts = False, dsrdtr = True, 
                            timeout = 0.1, write_timeout = 1.0, 
                            inter_byte_timeout = 0, exclusive = True)
    SerTram = serial.Serial(TRM_LGHT, 
                            baudrate = 115200, bytesize = 8, 
                            parity = 'N', rtscts = False, dsrdtr = True, 
                            timeout = 0.1, write_timeout = 1.0, 
                            inter_byte_timeout = 0, exclusive = True)
    sleep(0.050)
    print('R18: ' + str(RelayNum18))
    print('R916: ' + str(RelayNum916))
    print('Sound: ' + str(SOUND))
    print('(Not Required:  RelayNum3: ' + str(RelayNum3))
    print('Tram Lights: ' + str(TRM_LGHT))
    if not(ser18.is_open): 
            ser18.open()
    if not(ser916.is_open):
            ser916.open
    ser18.reset_output_buffer()
    ser916.reset_output_buffer()
    SerSound.reset_input_buffer()
    SerTram.reset_output_buffer()
    sleep(0.100)

    # Load TInyDB   & start RECEIVE for Server 
    #try:
        #if PIdb.count(all) > 80: 
    #PIdb.truncate() # clear db
    #except JSONDecodeError:
    #    if PIdb.count(all) > 80: 
    #        PIdb.truncate() # clear db        

    LoadDB()  # Load TinyDB & start RECEIVE for Server 

    receive_thread = threading.Thread(target=receive,daemon=True) #Start Receive
    receive_thread.start()
    sleep(1.000)
    handlePI_thread = threading.Thread(target=handlePI,daemon=True) # start handlePI
    handlePI_thread.start()

#^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#^^^^^^^^^^^^^^^^  MAIN LOOP ^^^^^^^^^^^^^^^^^^^^^^
#^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
while True:
    sleep(0.100) # give time for other things
    if not Timer2runb:
        tim2 = time.monotonic_ns()
        Timer2runb = True
    if time.monotonic_ns() - tim2 > 2000000000:         # to write the JSON file, every 2 sec for Speed
        tim2 = time.monotonic_ns()                      # others written when set
        Timer2secb, timer2runb = True, False
    else: Timer2secb = False
    # * Clear transmit registers *
    RHTholder = ''

# Go through local DB and see what HMI updated and get that values NEW
    for row in PIdb.search(query.HMI_READi == 2): 
        index = row.get("INDEX") 
        HMIValuei = row.get("HMI_VALUEi")
        HMIValueb = row.get("HMI_VALUEb")
    # update local DB

        match (index):          #   '0' is not in list, so will pass. than 49 will be passed also
            case 1: 
                HMI_RHT = HMIValuei     # integer
            case 2: 
                HMI_TramStopTime = HMIValuei    # integer
            case 3: HMI_AllQuietb = HMIValueb
            case 4: HMI_LIGHTONOFFb = HMIValueb
            case 5: 
                HMI_RR2_RR3Pwrb = HMIValueb
                if HMI_RR2_RR3Pwrb: RR2orRR3Pwr_HMIb = True
                else: RR2orRR3Pwr_HMIb = False
            case 6: HMI_RRBellb = HMIValueb
            case 7: HMI_RRDieselSteamb = HMIValueb
            case 8: HMI_RRHornb = HMIValueb
            case 9: HMI_RRQuietb = HMIValueb
            case 10: HMI_RRWhistleb = HMIValueb
            case 11: HMI_Switch1ABb = HMIValueb
            case 12: HMI_Switch2RR3b = HMIValueb
            case 13: HMI_Switch3RR4b = HMIValueb
            case 14: HMI_Switch4RR3b = HMIValueb
            case 15: HMI_Switch5ABb = HMIValueb
            case 16: HMI_Switch6ABb = HMIValueb
            case 17: HMI_TramQuietb = HMIValueb
            case 18: HMI_TramStpStn_2b = HMIValueb
            case 19: HMI_TramStpStn_3b = HMIValueb
            case 20: HMI_TramStpStn_5b = HMIValueb
            case 21: HMI_TramStpStn_6b = HMIValueb
            case 22: pass # Future inputs to 49
        PIdb.update({"HMI_READi": 0}, query.INDEX == index) # set read value to 0
    #Relay hold time - send to both
    if HMI_RHT != HMI_RHT_old:
        temp = ('RHT' + str(HMI_RHT))
        temp = temp.encode(FORMAT)
        RHTholder = temp
        SEND_MOD1(RHTholder)
        SEND_MOD2(RHTholder)
        HMI_RHT_old = HMI_RHT # record, don't send everytime
        
# Lights
    if HMI_LIGHTONOFFb != LightOldb:
        if HMI_LIGHTONOFFb:
            temp = 'LGHTON'							# TRUE = LIGHTS
            lightonoff = temp.encode(FORMAT)       
        else: 
            temp = 'LGTOFF'
            lightonoff = temp.encode(FORMAT)
        SEND_MOD2(lightonoff)
        LightOldb = HMI_LIGHTONOFFb
        
#  SWITCHES         send data to relay modules, Byte arrays
    # Module 1
    del switches1[0:72]                     # clears out byte array
    del switches2[0:72]                     # clears out byte array

    DictIndex = 53
    tag = 'Switch1Main_HMIb'
    PiValuef = 0.0
    if HMI_Switch1ABb and not Switch1Main_HMIb:       # SW 1 RR 1 to RR2 
        temp = bytes('M01R01', 'utf-8')
        switches1.extend(temp)
        Switch1Main_HMIb = True
        PIdb.update({"PI_VALUEb": Switch1Main_HMIb, "HMI_READi": 1}, query.INDEX == DictIndex)
        #print("Switch1Main_HMIb DB state after set 924 = ", PIdb.search(query.INDEX == 53))
    if not HMI_Switch1ABb and Switch1Main_HMIb: 
        temp = bytes('M01R02', 'utf-8')
        switches1.extend(temp)
        Switch1Main_HMIb = False
        PIdb.update({"PI_VALUEb": Switch1Main_HMIb, "HMI_READi": 1}, query.INDEX == DictIndex)
        print("Switch1Main_HMIb DB state after set 929 = ", PIdb.search(query.INDEX == 53))
    index = 55
    tag = 'Switch2RR3Main_HMIb'
    PiValuef = 0.0   
    if HMI_Switch2RR3b and not Switch2RR3Main_HMIb:
        temp = bytes('M01R03', 'utf-8')
        switches1.extend(temp)
        Switch2RR3Main_HMIb = True
        PiValueb = True
        PIdb.update({"PI_VALUEb": PiValueb, "HMI_VALUEi": 1}, query.INDEX == DictIndex) 
        
    if not HMI_Switch2RR3b and Switch2RR3Main_HMIb:
        temp = bytes('M01R04', 'utf-8')
        switches1.extend(temp)
        Switch2RR3Main_HMIb = False
        PiValueb = False
        PIdb.update({"PI_VALUEb": PiValueb, "HMI_VALUEi": 1}, query.INDEX == DictIndex) 
                
    DictIndex = 57
    tag = 'Switch3RR4Main_HMIb'
    PiValuef = 0.0
    if HMI_Switch3RR4b and not Switch3RR4Main_HMIb:
        temp = bytes('M01R05', 'utf-8')
        switches1.extend(temp)
        Switch3RR4Main_HMIb = True
        PiValueb = True
        PIdb.update({"PI_VALUEb": PiValueb, "HMI_VALUEi": 1}, query.INDEX == DictIndex) 
        
    if not HMI_Switch3RR4b and Switch3RR4Main_HMIb:
        temp = bytes('M01R06', 'utf-8')
        switches1.extend(temp)
        Switch3RR4Main_HMIb = False
        PiValueb = False
        PIdb.update({"PI_VALUEb": PiValueb, "HMI_VALUEi": 1}, query.INDEX == DictIndex) 
    
    DictIndex = 59
    tag = 'Switch4RR3Main_HMIb'
    PiValuef = 0.0    
    if not HMI_Switch4RR3b and not Switch4RR3Main_HMIb:
        temp = bytes('M01R07', 'utf-8')
        switches1.extend(temp)
        Switch4RR3Main_HMIb = True
        PiValueb = True
        PIdb.update({"PI_VALUEb": PiValueb, "HMI_VALUEi": 1}, query.INDEX == DictIndex) 
        
    if not HMI_Switch4RR3b and Switch4RR3Main_HMIb:
        temp = bytes('M01R08', 'utf-8')
        switches1.extend(temp)
        Switch4RR3Main_HMIb = False
        PiValueb = False
        PIdb.update({"PI_VALUEb": PiValueb, "HMI_VALUEi": 1}, query.INDEX == DictIndex)
   
    # Module 2
    DictIndex = 61
    tag = 'Switch5Main_HMIb'
    PiValuef = 0.0
    if HMI_Switch5ABb and not Switch5Main_HMIb: 
        temp = 'M02R09'
        temp = temp.encode(FORMAT)
        switches2.extend(temp)
        Switch5Main_HMIb = True
        PiValueb = True
        PIdb.update({"PI_VALUEb": PiValueb, "HMI_VALUEi": 1}, query.INDEX == DictIndex) 
                
    if not HMI_Switch5ABb and Switch5Main_HMIb: 
        temp = 'M02R10'
        temp = temp.encode(FORMAT)
        switches2.extend(temp)
        Switch5Main_HMIb = False
        PiValueb = False
        PIdb.update({"PI_VALUEb": PiValueb, "HMI_VALUEi": 1}, query.INDEX == DictIndex) 
    
    DictIndex = 63
    tag = 'Switch6Main_HMIb'
    PiValuef = 0.0         
    if HMI_Switch6ABb and not Switch6Main_HMIb:
        temp = 'M02R11'
        temp = temp.encode(FORMAT)
        switches2.extend(temp)
        Switch6Main_HMIb = True
        PiValueb = True
        PIdb.update({"PI_VALUEb": PiValueb, "HMI_VALUEi": 1}, query.INDEX == DictIndex) 
 
    if not HMI_Switch6ABb and Switch6Main_HMIb:
        temp = 'M02R12'
        temp = temp.encode(FORMAT)
        switches2.extend(temp)
        Switch6Main_HMIb = False
        PiValueb = False
        PIdb.update({"PI_VALUEb": PiValueb, "HMI_VALUEi": 1}, query.INDEX == DictIndex)
 
    if len(switches1) > 0:     #Send to relays if data
            SEND_MOD1(switches1)
            print(switches1)
            del switches1[0:72]                     # clears out byte array
    if len(switches2) > 0:      #Send to relays if have data
        SEND_MOD2(switches2)
        print(switches2)
        del switches2[0:72]                     # clears out byte array

#   TRAM - TELL TRAM PICO, HMI NOTIFICATION & SOUNDS 
#   TRAM - Tramdetected and only single shot & HMI seleted to stop there   
    if not Tram1Stopbg and not TramStop1.is_active: TramStop1.when_deactivated = TramStationArrive(1)  # NOT EDGE TRIGGER 
    if Tram1Stopbg and TramStop1.is_active: TramStop1.when_activated = TramStationDepart(1)  # not EDGE TRIGGER
    if not Tram2Stopbg and not TramStop2.is_active and HMI_TramStpStn_2b:TramStop2.when_deactivated = TramStationArrive(2)
    if Tram2Stopbg and TramStop2.is_active and HMI_TramStpStn_2b:TramStop2.when_activated = TramStationDepart(2)   
    if not Tram3Stopbg and not TramStop3.is_active and HMI_TramStpStn_3b:TramStop3.when_deactivated = TramStationArrive(3)
    if Tram3Stopbg and TramStop3.is_active and TramStop3.when_activated and HMI_TramStpStn_3b:TramStop3.when_deactivated= TramStationDepart(3)
    if not Tram4Stopbg and not TramStop4.is_active:TramStop4.when_deactivated = TramStationArrive(4)
    if Tram4Stopbg and TramStop4.is_active:TramStop4.when_activated = TramStationDepart(4) 
    if not Tram5Stopbg and not TramStop5.is_active and HMI_TramStpStn_5b:TramStop5.when_deactivated = TramStationArrive(5)
    if Tram5Stopbg and TramStop5.is_active and HMI_TramStpStn_5b:TramStop6.when_activated = TramStationDepart(5)
    if not Tram6Stopbg and not TramStop6.is_active and HMI_TramStpStn_6b:TramStop6.when_deactivated = TramStationArrive(6)
    if Tram6Stopbg and TramStop6.is_active and HMI_TramStpStn_6b:TramStop6.when_activated = TramStationDepart(6)     

# CALCULATE SPEED
 #IN MPH. 2 inches apart on sensors. DISPLAY NEAR LOCATION of SENSORS
# alarming if to high mph SAM
    if (not RR1Aspeed.light_detected or not RR1Bspeed.light_detected) and not RR1ABTmrb: 
        RR1ABstrt =time.monotonic()
        RR1ABTmrb = True
    if not RR1Aspeed.light_detected and not RR1Bspeed.light_detected:
        RR1ABend = time.monotonic()
        temp = 9980.0/abs(RR1ABend - RR1ABstrt)
        RR1ABTmrb = False
        if temp > 99.0: RR1ABspeed_HMI = 0.66  	# speed error	
    else: RR1ABspeed_HMI = round(temp,2)
        
    if (not RR1Cspeed.light_detected or not RR1Dspeed.light_detected) and not RR1CDTmrb: 
        RR1CDstrt =time.monotonic()
        RR1CDTmrb = True
    if not RR1Cspeed.light_detected and not RR1Dspeed.light_detected:
        RR1CDend = time.monotonic()
        temp = 9980.0/abs(RR1CDend - RR1CDstrt)
        RR1CDTmrb = False
        if  temp > 99.0: RR1CDspeed_HMI = 0.66 	#speed error
        else: RR1CDspeed_HMI = round(temp, 2)	
          
    if (not RR2Aspeed.light_detected or not RR2Bspeed.light_detected) and  not RR2ABTmrb: 
        RR2ABstrt=time.monotonic()
        RR2ABTmrb = True
    if not RR2Aspeed.light_detected and not RR2Bspeed.light_detected and RR2ABTmrb: 
        RR2ABtime=9980.0/abs(time.monotonic()-RR2ABstrt) # for 2" sensor separation, monotonic in ms, so * 1000
        RR2ABTmrb = False 
        if temp > 99.0: RR2ABspeed_HMI = 0.66  #speed error alarming if to high, for HMI
        else: RR2ABspeed_HMI = round(temp,2)
        
    if Timer2secb:          # 2 seconds over, update JSON with speed
        PIdb.update({"PI_VALUEf": RR1ABspeed_HMI, "HMI_VALUEi": 1}, query.TAG == "RR1ABspeed_HMI")
        PIdb.update({"PI_VALUEf": RR1CDspeed_HMI, "HMI_VALUEi": 1}, query.TAG == "RR1CDspeed_HMI")
        PIdb.update({"PI_VALUEf": RR2ABspeed_HMI, "HMI_VALUEi": 1}, query.TAG == "RR2ABspeed_HMI")

    # PUSH BUTTONS
    GrpPBb = (PButton1.is_active and not button1b) or (PButton2.is_active and not button2b) or (PButton3.is_active and not button3b) or (PButton4.is_active and not button4b) or (PButton5.is_active and not button5b)
    if GrpPBb:
        jj = random.randint(1, 14)
        match jj:
            case 1: StmWhistle.play()             # make a sound for each PB, independent of LEDs
            case 2: StmBell.play()
            case 3: DslHorn.play()
            case 4: woohoo.play()
            case 5: clap.play()
            case 6: siren1.play()
            case 7: siren2.play()
            case 8: siren3.play()
            case 9: siren4.play()
            case 10: zapWhistle.play()
            case 11: Laughter.play()
            case 12: Beep.play()
            case 13: Blast.play()
            case 14: Beep3.play()
        # Pressing buttons 
        PBSelecti = 9          # in case of fast fingers and miss pushbottom.is active for PBSelecti
        if LEDsCompleteb:                  # boolean that LEDs are completed, ready for next input
            LEDsCompleteb = False          # NeoRandomb set by functions       
        if PButton1.is_active:
            PBSelecti = 1
            button1b = True     # kids may keep button pressed
        elif PButton2.is_active: 
            PBSelecti = 2
            button2b = True     # prevents queuing of sounds
        elif PButton3.is_active: 
            PBSelecti = 3
            button3b = True
        elif PButton4.is_active: 
            PBSelecti = 4
            button4b = True
        elif PButton5.is_active: 
            PBSelecti = 5
            button5b = True
        NeoRandom(PBSelecti)                    
    else: 
         if not PButton1.is_active: button1b = False
         if not PButton2.is_active: button2b = False
         if not PButton3.is_active: button3b = False
         if not PButton4.is_active: button4b = False
         if not PButton5.is_active: button5b = False
    # Play Train Souonds from HMI input, 1 time each
    PiPlayTrainMusic()
    if HMI_RRHornb: 
        DslHorn.play()
        HMI_RRHornb = False
    if HMI_RRWhistleb: 
        StmWhistle.play()
        HMI_RRWhistleb = False
    if HMI_RRBellb: 
        StmBell.play()
        HMI_RRBellb = False
#   For selecting RR2 or RR3 for the left power supply
    if HMI_RR2_RR3Pwrb: RR2orRR3.value = True
    else: RR2orRR3.value=False
   
