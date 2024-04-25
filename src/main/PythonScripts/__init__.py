import subprocess
import json

# Start the test here. This is a python dictionary that contains all of the values.
x = {
    0 : 0, # Tells Pi to get data. 0, dad reads. He sets to 1. For 2, I read it on java.
    1 : 0.12, # RR1ABspeed_HMI
    2 : 0.12, # RR1CDspeed_HMI
    3 : 0.12, # RR2ABspeed_HMI
    4 : False, # Switch1Main_HMIb
    5 : False, # Switch1RR2RR3_HMIb
    6 : False, # Switch2RR3Main_HMIb
    7 : False, # Switch2RR3RR4_HMIb
    8 : False, # Switch3RR4Main_HMIb
    9 : False, # Switch2RR3Main_HMIb
    10 : False, # Switch3RR4Spur_HMIb
    11 : False, # Switch4RR3Main_HMIb
    12 : False, # Switch4RR3RR4_HMIb
    13 : False, # Switch5Main_HMIb
    14 : False, # Switch5RR2RR3_HMIb
    15 : False, # Switch6Main_HMIb
    16 : False, # Switch6RR1RR2_HMIb
    17 : False, # TramStn1_HMIb
    18 : False, # TramStn2_HMIb
    19 : False, # TramStn3_HMIb
    20 : False, # TramStn4_HMIb
    21 : False, # TramStn5_HMIb
    22 : False, # TramStn6_HMIb
    50 : False, # RR1ABspeed_HMI
    51 : False, # RR1CDspeed_HMI
    52 : False, # RR2ABspeed_HMI
    53 : False, # Switch1Main_HMIb
    54 : False, # Switch1RR2RR3_HMIb
    55 : False, # Switch2RR3Main_HMIb
    56 : False, # Switch2RR3RR4_HMIb
    57 : False, # Switch3RR4Main_HMIb
    58 : False, # Switch3RR4Spur_HMIb
    59 : False, # Switch4RR3Main_HMIb
    60 : False, # Switch4RR3RR4_HMIb
    61 : False, # Switch5Main_HMIb
    62 : False, # Switch5RR2RR3_HMIb
    63 : False, # Switch6Main_HMIb
    64 : False, # Switch6RR1RR2_HMIb
    65 : False, # TramStn1_HMIb
    66 : False, # TramStn2_HMIb
    67 : False, # TramStn3_HMIb
    68 : False, # TramStn4_HMIb
    69 : False, # TramStn5_HMIb
    70 : False, # TramStn6_HMIb
}

x_to_json = json.dumps(x)

print(type(x_to_json))
print(x_to_json)

json_to_dict = json.loads(x_to_json)

print(type(json_to_dict))
print(json_to_dict)

# print('type of variable at 0 is: ')
# type(x["0"])
# p = subprocess.Popen("java -jar 'name the jar here'" stdin=subprocess.PIPE, stdout=subprocess.PIPE)

# import subprocess
# import json
# #   Not sure how the data comes in. Need to understand that first
#
#
# RR1ABspeed_HMI = 0.12
# RR1CDspeed_HMI = 0.12
# RR2ABspeed_HMI = 0.12
# Switch1Main_HMIb = False
# Switch1RR2RR3_HMIb = False
# Switch2RR3Main_HMIb = False
# Switch2RR3RR4_HMIb = False
# Switch3RR4Main_HMIb = False
# Switch2RR3Main_HMIb = False
# Switch3RR4Spur_HMIb = False
# Switch4RR3Main_HMIb = False
# Switch4RR3RR4_HMIb = False
# Switch5Main_HMIb = False
# Switch5RR2RR3_HMIb = False
# Switch6Main_HMIb = False
# Switch6RR1RR2_HMIb = False
# TramStn1_HMIb = False
# TramStn2_HMIb = False
# TramStn3_HMIb = False
# TramStn4_HMIb = False
# TramStn5_HMIb = False
# TramStn6_HMIb = False
#
# PIIndex = 50        #   This is used to control the sending item index number
#
# HMItoPI = subprocess.Popen("java -jar" "SAMUEL??.jar",    #  SAM HELP ON NAME PLEASE
#                            stdin = subprocess.PIPE,
#                            stdout = subprocess.PIPE)
#
# match int(HMItoPI['INDEX']):          #   '0' is not in list, so will pass. those reater than 49 will be passed also
#     case 1:                         # integer
#         RHT_HMI = HMItoPI["HMI_VALUEi"]      # JSON sends INTEGER value
#         print('HMI Sent '+ str(HMItoPI['INDEX']) + ' RHT_HMI = ', str(RHT_HMI))
#     case 2:                         # integer
#         HMI_TramStopTime = HMItoPI["HMI_VALUEi"]
#         print('HMI Sent '+ str(HMItoPI['INDEX']) + ' HMI_TramStopTime = ', str(HMI_TramStopTime))
#     case 3:
#         HMI_AllQuietb = HMItoPI["HMI_VALUEb"]
#         print('HMI Sent '+ str(HMItoPI['INDEX']) + ' HMI_AllQuietb = ', HMI_AllQuietb)
#     case 4:
#         HMI_LIGHTONOFFb = HMItoPI["HMI_VALUEb"]
#         print('HMI Sent '+ str(HMItoPI['INDEX']) + ' HMI_LIGHTONOFFb = ', HMI_LIGHTONOFFb)
#     case 5:
#         HMI_RR2_RR3Pwrb = HMItoPI["HMI_VALUEb"]
#         print('HMI Sent '+ str(HMItoPI['INDEX']) + ' HMI_RR2_RR3Pwrb = ', HMI_RR2_RR3Pwrb)
#     case 6:
#         HMI_RRBellb = HMItoPI["HMI_VALUEb"]
#         print('HMI Sent '+ str(HMItoPI['INDEX']) + ' HMI_RRBellb = ', HMI_RRBellb)
#     case 7:
#         HMI_RRDieselSteamb = HMItoPI["HMI_VALUEb"]
#         print('HMI Sent '+ str(HMItoPI['INDEX']) + ' HMI_RRDieselSteamb = ', HMI_RRDieselSteamb)
#     case 8:
#         HMI_RRHornb = HMItoPI["HMI_VALUEb"]
#         print('HMI Sent '+ str(HMItoPI['INDEX']) + ' HMI_RRHornb = ', HMI_RRHornb)
#     case 9:
#         HMI_RRQuietb = HMItoPI["HMI_VALUEb"]
#         print('HMI Sent '+ str(HMItoPI['INDEX']) + ' HMI_RRQuietb = ', HMI_RRQuietb)
#     case 10:
#         HMI_RRWhistleb = HMItoPI["HMI_VALUEb"]
#         print('HMI Sent '+ str(HMItoPI['INDEX']) + ' HMI_RRWhistleb = ', HMI_RRWhistleb)
#     case 11:
#         HMI_Switch1ABb = HMItoPI["HMI_VALUEb"]
#         print('HMI Sent '+ str(HMItoPI['INDEX']) + ' HMI_Switch1ABb = ', HMI_Switch1ABb)
#     case 12:
#         HMI_Switch2RR3b = HMItoPI["HMI_VALUEb"]
#         print('HMI Sent '+ str(HMItoPI['INDEX']) + ' HMI_Switch2RR3b = ', HMI_Switch2RR3b)
#     case 13:
#         HMI_Switch3RR4b = HMItoPI["HMI_VALUEb"]
#         print('HMI Sent '+ str(HMItoPI['INDEX']) + ' HMI_Switch3RR4b = ', HMI_Switch3RR4b)
#     case 14:
#         HMI_Switch4RR3b = HMItoPI["HMI_VALUEb"]
#         print('HMI Sent '+ str(HMItoPI['INDEX']) + ' HMI_Switch4RR3b = ', HMI_Switch4RR3b)
#     case 15:
#         HMI_Switch5ABb = HMItoPI["HMI_VALUEb"]
#         print('HMI Sent '+ str(HMItoPI['INDEX']) + ' HMI_Switch5ABb = ', HMI_Switch5ABb)
#     case 16:
#         HMI_Switch6ABb = HMItoPI["HMI_VALUEb"]
#         print('HMI Sent '+ str(HMItoPI['INDEX']) + ' HMI_Switch6ABb = ', HMI_Switch6ABb)
#     case 17:
#         HMI_TramQuietb = HMItoPI["HMI_VALUEb"]
#         print('HMI Sent '+ str(HMItoPI['INDEX']) + ' HMI_TramQuietb = ', HMI_TramQuietb)
#     case 18:
#         HMI_TramStpStn_2b = HMItoPI["HMI_VALUEb"]
#         print('HMI Sent '+ str(HMItoPI['INDEX']) + ' HMI_TramStpStn_2b = ', HMI_TramStpStn_2b)
#     case 19:
#         HMI_TramStpStn_3b = HMItoPI["HMI_VALUEb"]
#         print('HMI Sent '+ str(HMItoPI['INDEX']) + ' HMI_TramStpStn_3b = ', HMI_TramStpStn_3b)
#     case 20:
#         HMI_TramStpStn_5b = HMItoPI["HMI_VALUEb"]
#         print('HMI Sent '+ str(HMItoPI['INDEX']) + ' HMI_TramStpStn_5b = ', HMI_TramStpStn_5b)
#     case 21:
#         HMI_TramStpStn_6b = HMItoPI["HMI_VALUEb"]
#         print('HMI Sent '+ str(HMItoPI['INDEX']) + ' HMI_TramStpStn_6b = ', HMI_TramStpStn_6b)
#     case 22:
#         pass    #   future inputs to 49
#     #      Tell HMI that PI got the data
# if HMItoPI['INDEX'] !=0 or HMItoPI["PI_READi"] == 1:    # Send only if read message AND NEED TO ACKNOWLEDGE HMI
#     PISend = {"INDEX":0, "HMI_VALUEi": 0,
#               "HMI_VALUEb": None, "PI_VALUEb": None,
#               "PI_VALUEf": 0.33, "PI_READi": 2}      # SAMMY DO I NEED TO CLEAR VALUES, I AM USING 3 TO TELL YOU I HAVE READ IT
#     HMItoPI, e = HMItoPI.communicate(json.dumps([PISend]))
#
# #   SAM YOU WILL HAVE TO SET PI_READ TO False UPON READING. PI DOES NOTHING WITH IT EXPECT FOR TIMING
#
# #   CAN WE CREATE A LIST OR PI MONITOR A HMI_READ BIT. DONT WANT TO HANG
# #       PROGRAM TOO LONG. MAY BE CONCURRENT PROCESS IS TO BE USED BY PI
#
# if not HMItoPI["PI_READ"]:      # SEE ABOVE QUESTIONS ABOUT HOW hmi HANDLES? only send when HMI resets PI_READ (False)
#     #   there will be multiple lines mainly at the startup. PAUL - how to handle, detect extra lines, remove read line????
#
#     x = input("input INDEX 50 to 70, default is 53 (boolean)")
#     if x == 0: x=53
#     if x < 50 or x > 70:
#         y = input("using 53, Switch1Main_HMIb, will flip, present value is " + Switch1Main_HMIb + 'hit enter')
#         y = not Switch1Main_HMIb
#     if x > 49 and x < 53:
#         match x:
#             case 50: y = input("using " + x + ' RR1ABspeed_HMI present value is ' + RR1ABspeed_HMI + 'enter value')
#             case 51: y = input("using " + x + ' RR1CDspeed_HMI present value is ' + RR1CDspeed_HMI + 'enter value')
#             case 52: y = input("using " + x + ' RR2ABspeed_HMI present value is ' + RR2ABspeed_HMI + 'enter value')
#         HMItoPI, e = HMItoPI.communicate(json.dumps({"INDEX": x, "PI_VALUEf": y}))
#         if x > 52 and x < 71:
#
#             x = input("using " + x + " will flip - hit enter")
#             y = not Switch1Main_HMIb
#         match x:  # Below may be moved to where values are set in program. else have to track old value and send new value
#             case 53: name = Switch1Main_HMIb
#             case 54: name = Switch1RR2RR3_HMIb
#             case 55: name = Switch2RR3Main_HMIb
#             case 56: name = Switch2RR3Main_HMIb
#             case 57: name = Switch3RR4Main_HMIb
#             case 58: name = Switch3RR4Spur_HMIb
#             case 59: name = Switch4RR3Main_HMIb
#             case 60: name = Switch4RR3RR4_HMIb
#             case 61: name = Switch5Main_HMIb
#             case 62: name = Switch5RR2RR3_HMIb
#             case 63: name = Switch6Main_HMIb
#             case 64: name = Switch6RR1RR2_HMIb
#             case 65: name = TramStn1_HMIb
#             case 66: name = TramStn2_HMIb
#             case 67: name = TramStn3_HMIb
#             case 68: name = TramStn4_HMIb
#             case 69: name = TramStn5_HMIb
#             case 70: name = TramStn6_HMIb
#         y = not name
#         HMItoPI, e = HMItoPI.communicate(json.dumps({"INDEX": x, "PI_VALUEb": y, "PI_READI": 2}))