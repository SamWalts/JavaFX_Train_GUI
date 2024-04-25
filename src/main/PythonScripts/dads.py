import json
import subprocess
from json import dumps as json_dumps, loads as json_loads
# from abc import ABC, abstractmethod

def JsonWriter(Dictname, filename: str):
    with open(filename, "w") as fp:
        json.dump(Dictname , fp, indent = 4)

def JsonReader(filename: str):
    with open(filename) as f_in:
        return json.load(f_in)

def DictIterator(dictObj, v):
    for value in dictObj.values():
        if isinstance(value, dict):
            for v in dictObj(value): yield v
        else: yield value

def FromHmiPrint(Name, Value):
    print('HMI Sent for ', Name, ' HMI_AllQuietb = ', Value)

#    The PI_READi is: 0 = nothing new, 1 = HMI changed this line, 2 = PI changed this line
#    Collect indexes for changed items and collect the value of the change
Index = 0      # index of the dictionary being querried
DictLine = []   # Converted line from dictionary Line - LIST
HMIValuei = 0  # Hold HMI value
HMIValueb = False  # Hold HMI value

if __name__ == "__main__":
    #    Define Registers
    Index = 0      # index of the dictionary being querried
    DictLine = []   # Converted line from dictionary Line - LIST
    DictTemp = {}   # temp to hold a line from dictionary
    HMIValuei = 0  # Hold HMI value for PI
    HMIValueb = False  # Hold HMI value for PI
    PIValuef = 0  # Hold PI value for HMI
    PIValueb = False  # Hold PI value for HMI
    v = "HMI"

    #    save initial dictionary - only upon startup
    #   Load initial and the not use again read from then on
    x = input("create initial Dictionary & write to disk? 'y' to load or anykey: ")
    if x == 'y' or x == 'Y':
        HMItoPIDict = {
            "1": {"TAG":"HMI_RHT", "HMI_VALUEi": 123, "HMI_VALUEb": False, "PI_VALUEf": 0.0, "PI_VALUEb": None, "HMI_READi": 1},
            "2": {"TAG":"HMI_TramStopTime", "HMI_VALUEi": 10, "HMI_VALUEb": True, "PI_VALUEf": 0.0, "PI_VALUEb": None, "HMI_READi": 0},
            "3": {"TAG":"HMI_AllQuietb", "HMI_VALUEi": 0, "HMI_VALUEb": False, "PI_VALUEf": 0.0, "PI_VALUEb": None, "HMI_READi": 1},
            "4": {"TAG":"HMI_LIGHTONOFFb", "HMI_VALUEi": 0, "HMI_VALUEb": True, "PI_VALUEf": 0.0, "PI_VALUEb": None, "HMI_READi": 0},
            "5": {"TAG":"HMI_RR2_RR3Pwrb", "HMI_VALUEi": 0, "HMI_VALUEb": True, "PI_VALUEf": 0.0, "PI_VALUEb": None, "HMI_READi": 1},
            "6": {"TAG":"HMI_RRBellb", "HMI_VALUEi": 0, "HMI_VALUEb": True, "PI_VALUEf": 0.0, "PI_VALUEb": None, "HMI_READi": 0},
            "7": {"TAG":"HMI_RRDieselSteamb", "HMI_VALUEi": 0, "HMI_VALUEb": False, "PI_VALUEf": 0.0, "PI_VALUEb": None, "HMI_READi": 0},
            "8": {"TAG":"HMI_RRHornb", "HMI_VALUEi": 0, "HMI_VALUEb": True, "PI_VALUEf": 0.0, "PI_VALUEb": None, "HMI_READi": 0},
            "9": {"TAG":"HMI_RRQuietb", "HMI_VALUEi": 0, "HMI_VALUEb": False, "PI_VALUEf": 0.0, "PI_VALUEb": None, "HMI_READi": 0},
            "10": {"TAG":"HMI_RRWhistleb", "HMI_VALUEi": 0, "HMI_VALUEb": True, "PI_VALUEf": 0.0, "PI_VALUEb": None, "HMI_READi": 0},
            "11": {"TAG":"HMI_Switch1ABb", "HMI_VALUEi": 0, "HMI_VALUEb": True, "PI_VALUEf": 0.0, "PI_VALUEb": None, "HMI_READi": 0},
            "12": {"TAG":"HMI_Switch2RR3b", "HMI_VALUEi": 0, "HMI_VALUEb": True, "PI_VALUEf": 0.0, "PI_VALUEb": None, "HMI_READi": 0},
            "13": {"TAG":"HMI_Switch3RR4b", "HMI_VALUEi": 0, "HMI_VALUEb": False, "PI_VALUEf": 0.0, "PI_VALUEb": None, "HMI_READi": 0},
            "14": {"TAG":"HMI_Switch4RR3b", "HMI_VALUEi": 0, "HMI_VALUEb": True, "PI_VALUEf": 0.0, "PI_VALUEb": None, "HMI_READi": 0},
            "15": {"TAG":"HMI_Switch5ABb", "HMI_VALUEi": 0, "HMI_VALUEb": False, "PI_VALUEf": 0.0, "PI_VALUEb": None, "HMI_READi": 0},
            "16": {"TAG":"HMI_Switch6ABb", "HMI_VALUEi": 0, "HMI_VALUEb": True, "PI_VALUEf": 0.0, "PI_VALUEb": None, "HMI_READi": 0},
            "17": {"TAG":"HMI_TramQuietb", "HMI_VALUEi": 0, "HMI_VALUEb": True, "PI_VALUEf": 0.0, "PI_VALUEb": None, "HMI_READi": 0},
            "18": {"TAG":"HMI_TramStpStn_2b", "HMI_VALUEi": 0, "HMI_VALUEb": True, "PI_VALUEf": 0.0, "PI_VALUEb": None, "HMI_READi": 0},
            "19": {"TAG":"HMI_TramStpStn_3b", "HMI_VALUEi": 0, "HMI_VALUEb": False, "PI_VALUEf": 0.0, "PI_VALUEb": None, "HMI_READi": 0},
            "20": {"TAG":"HMI_TramStpStn_5b", "HMI_VALUEi": 0, "HMI_VALUEb": True, "PI_VALUEf": 0.0, "PI_VALUEb": None, "HMI_READi": 0},
            "21": {"TAG":"HMI_TramStpStn_6b", "HMI_VALUEi": 0, "HMI_VALUEb": False, "PI_VALUEf": 0.0, "PI_VALUEb": None, "HMI_READi": 0},
            "22": {"TAG":"HMI_Future_1", "HMI_VALUEi": 0, "HMI_VALUEb": True, "PI_VALUEf": 0.0, "PI_VALUEb": None, "HMI_READi": 0},
            "23": {"TAG":"HMI_Future_2", "HMI_VALUEi": 0, "HMI_VALUEb": True, "PI_VALUEf": 0.0, "PI_VALUEb": None, "HMI_READi": 0},
            "24": {"TAG":"HMI_Future_3", "HMI_VALUEi": 0, "HMI_VALUEb": True, "PI_VALUEf": 0.0, "PI_VALUEb": None, "HMI_READi": 0},
            "25": {"TAG":"HMI_Future_4", "HMI_VALUEi": 0, "HMI_VALUEb": True, "PI_VALUEf": 0.0, "PI_VALUEb": None, "HMI_READi": 0},
            "26": {"TAG":"HMI_Future_5", "HMI_VALUEi": 0, "HMI_VALUEb": True, "PI_VALUEf": 0.0, "PI_VALUEb": None, "HMI_READi": 0},
            "27": {"TAG":"HMI_Future_6", "HMI_VALUEi": 0, "HMI_VALUEb": True, "PI_VALUEf": 0.0, "PI_VALUEb": None, "HMI_READi": 0},
            "28": {"TAG":"HMI_Future_7", "HMI_VALUEi": 0, "HMI_VALUEb": True, "PI_VALUEf": 0.0, "PI_VALUEb": None, "HMI_READi": 0},
            "29": {"TAG":"HMI_Future_8", "HMI_VALUEi": 0, "HMI_VALUEb": True, "PI_VALUEf": 0.0, "PI_VALUEb": None, "HMI_READi": 0},
            "30": {"TAG":"HMI_Future_9", "HMI_VALUEi": 0, "HMI_VALUEb": True, "PI_VALUEf": 0.0, "PI_VALUEb": None, "HMI_READi": 0},
            "31": {"TAG":"HMI_Future_10", "HMI_VALUEi": 0, "HMI_VALUEb": True, "PI_VALUEf": 0.0, "PI_VALUEb": None, "HMI_READi": 0},
            "32": {"TAG":"HMI_Future_11", "HMI_VALUEi": 0, "HMI_VALUEb": True, "PI_VALUEf": 0.0, "PI_VALUEb": None, "HMI_READi": 0},
            "33": {"TAG":"HMI_Future_12", "HMI_VALUEi": 0, "HMI_VALUEb": True, "PI_VALUEf": 0.0, "PI_VALUEb": None, "HMI_READi": 0},
            "34": {"TAG":"HMI_Future_13", "HMI_VALUEi": 0, "HMI_VALUEb": True, "PI_VALUEf": 0.0, "PI_VALUEb": None, "HMI_READi": 0},
            "35": {"TAG":"HMI_Future_14", "HMI_VALUEi": 0, "HMI_VALUEb": True, "PI_VALUEf": 0.0, "PI_VALUEb": None, "HMI_READi": 0},
            "36": {"TAG":"HMI_Future_15", "HMI_VALUEi": 0, "HMI_VALUEb": True, "PI_VALUEf": 0.0, "PI_VALUEb": None, "HMI_READi": 0},
            "37": {"TAG":"HMI_Future_16", "HMI_VALUEi": 0, "HMI_VALUEb": True, "PI_VALUEf": 0.0, "PI_VALUEb": None, "HMI_READi": 0},
            "38": {"TAG":"HMI_Future_17", "HMI_VALUEi": 0, "HMI_VALUEb": True, "PI_VALUEf": 0.0, "PI_VALUEb": None, "HMI_READi": 0},
            "39": {"TAG":"HMI_Future_18", "HMI_VALUEi": 0, "HMI_VALUEb": True, "PI_VALUEf": 0.0, "PI_VALUEb": None, "HMI_READi": 0},
            "40": {"TAG":"HMI_Future_19", "HMI_VALUEi": 0, "HMI_VALUEb": True, "PI_VALUEf": 0.0, "PI_VALUEb": None, "HMI_READi": 0},
            "41": {"TAG":"HMI_Future_20", "HMI_VALUEi": 0, "HMI_VALUEb": True, "PI_VALUEf": 0.0, "PI_VALUEb": None, "HMI_READi": 0},
            "42": {"TAG":"HMI_Future_21", "HMI_VALUEi": 0, "HMI_VALUEb": True, "PI_VALUEf": 0.0, "PI_VALUEb": None, "HMI_READi": 0},
            "43": {"TAG":"HMI_Future_22", "HMI_VALUEi": 0, "HMI_VALUEb": True, "PI_VALUEf": 0.0, "PI_VALUEb": None, "HMI_READi": 0},
            "44": {"TAG":"HMI_Future_23", "HMI_VALUEi": 0, "HMI_VALUEb": True, "PI_VALUEf": 0.0, "PI_VALUEb": None, "HMI_READi": 0},
            "45": {"TAG":"HMI_Future_24", "HMI_VALUEi": 0, "HMI_VALUEb": True, "PI_VALUEf": 0.0, "PI_VALUEb": None, "HMI_READi": 0},
            "46": {"TAG":"HMI_Future_25", "HMI_VALUEi": 0, "HMI_VALUEb": True, "PI_VALUEf": 0.0, "PI_VALUEb": None, "HMI_READi": 0},
            "47": {"TAG":"HMI_Future_26", "HMI_VALUEi": 0, "HMI_VALUEb": True, "PI_VALUEf": 0.0, "PI_VALUEb": None, "HMI_READi": 0},
            "48": {"TAG":"HMI_Future_27", "HMI_VALUEi": 0, "HMI_VALUEb": True, "PI_VALUEf": 0.0, "PI_VALUEb": None, "HMI_READi": 0},
            "49": {"TAG":"HMI_Future_28", "HMI_VALUEi": 0, "HMI_VALUEb": True, "PI_VALUEf": 0.0, "PI_VALUEb": None, "HMI_READi": 0},

            "50": {"TAG":"RR1ABspeed_HMI", "HMI_VALUEi": 0, "HMI_VALUEb": None, "PI_VALUEf": 0.12, "PI_VALUEb": None, "HMI_READi": 0},
            "51": {"TAG":"RR1CDspeed_HMI", "HMI_VALUEi": 0, "HMI_VALUEb": None, "PI_VALUEf": 0.12, "PI_VALUEb": None, "HMI_READi": 0},
            "52": {"TAG":"RR2ABspeed_HMI", "HMI_VALUEi": 0, "HMI_VALUEb": None, "PI_VALUEf": 0.12, "PI_VALUEb": None, "HMI_READi": 0},
            "53": {"TAG":"Switch1Main_HMIb", "HMI_VALUEi": 0, "HMI_VALUEb": None, "PI_VALUEf": 0.12, "PI_VALUEb": False, "HMI_READi": 0},
            "54": {"TAG":"open", "HMI_VALUEi": 0, "HMI_VALUEb": None, "PI_VALUEf": 0.12, "PI_VALUEb": False, "HMI_READi": 0},
            "55": {"TAG":"Switch2RR3Main_HMIb", "HMI_VALUEi": 0, "HMI_VALUEb": None, "PI_VALUEf": 0.12, "PI_VALUEb": False, "HMI_READi": 0},
            "56": {"TAG":"open", "HMI_VALUEi": 0, "HMI_VALUEb": None, "PI_VALUEf": 0.12, "PI_VALUEb": False, "HMI_READi": 0},
            "57": {"TAG":"Switch3RR4Main_HMIb", "HMI_VALUEiy": 0, "HMI_VALUEb": None, "PI_VALUEf": 0.12, "PI_VALUEb": True, "HMI_READi": 0},
            "58": {"TAG":"open", "HMI_VALUEi": 0, "HMI_VALUEb": None, "PI_VALUEf": 0.12, "PI_VALUEb": False, "HMI_READi": 0},
            "59": {"TAG":"Switch4RR3Main_HMIb", "HMI_VALUEi": 0, "HMI_VALUEb": None, "PI_VALUEf": 0.12, "PI_VALUEb": False, "HMI_READi": 0},
            "60": {"TAG":"open", "HMI_VALUEi": 0, "HMI_VALUEb": None, "PI_VALUEf": 0.12, "PI_VALUEb": False, "HMI_READi": 0},
            "61": {"TAG":"Switch5Main_HMIb", "HMI_VALUEi": 0, "HMI_VALUEb": None, "PI_VALUEf": 0.12, "PI_VALUEb": False, "HMI_READi": 0},
            "62": {"TAG":"open", "HMI_VALUEi": 0, "HMI_VALUEb": None, "PI_VALUEf": 0.12, "PI_VALUEb": True, "HMI_READi": 0},
            "63": {"TAG":"Switch6Main_HMIb", "HMI_VALUEi": 0, "HMI_VALUEb": None, "PI_VALUEf": 0.12, "PI_VALUEb": False, "HMI_READi": 0},
            "64": {"TAG":"open", "HMI_VALUEi": 0, "HMI_VALUEb": None, "PI_VALUEf": 0.12, "PI_VALUEb": False, "HMI_READi": 0},
            "65": {"TAG":"TramStn1_HMIb", "HMI_VALUEi": 0, "HMI_VALUEb": None, "PI_VALUEf": 0.12, "PI_VALUEb": False, "HMI_READi": 0},
            "66": {"TAG":"TramStn2_HMIb", "HMI_VALUEi": 0, "HMI_VALUEb": None, "PI_VALUEf": 0.12, "PI_VALUEb": False, "HMI_READi": 0},
            "67": {"TAG":"TramStn3_HMIb", "HMI_VALUEi": 0, "HMI_VALUEb": None, "PI_VALUEf": 0.12, "PI_VALUEb": False, "HMI_READi": 0},
            "68": {"TAG":"TramStn4_HMIb", "HMI_VALUEi": 0, "HMI_VALUEb": None, "PI_VALUEf": 0.12, "PI_VALUEb": True, "HMI_READi": 0},
            "69": {"TAG":"TramStn5_HMIb", "HMI_VALUEi": 0, "HMI_VALUEb": None, "PI_VALUEf": 0.12, "PI_VALUEb": False, "HMI_READi": 0},
            "70": {"TAG":"TramStn6_HMIb", "HMI_VALUEi": 0, "HMI_VALUEb": None, "PI_VALUEf": 0.12, "PI_VALUEb": False, "HMI_READi": 0},
            "71": {"TAG":"PI_Future_1", "HMI_VALUEi": 0, "HMI_VALUEb": None, "PI_VALUEf": 0.12, "PI_VALUEb": False, "HMI_READi": 0},
            "72": {"TAG":"PI_Future_2", "HMI_VALUEi": 0, "HMI_VALUEb": None, "PI_VALUEf": 0.12, "PI_VALUEb": False, "HMI_READi": 0},
            "73": {"TAG":"PI_Future_3", "HMI_VALUEi": 0, "HMI_VALUEb": None, "PI_VALUEf": 0.12, "PI_VALUEb": False, "HMI_READi": 0},
            "74": {"TAG":"PI_Future_4", "HMI_VALUEi": 0, "HMI_VALUEb": None, "PI_VALUEf": 0.12, "PI_VALUEb": False, "HMI_READi": 0},
            "75": {"TAG":"PI_Future_5", "HMI_VALUEi": 0, "HMI_VALUEb": None, "PI_VALUEf": 0.12, "PI_VALUEb": False, "HMI_READi": 0},
            "76": {"TAG":"PI_Future_6", "HMI_VALUEi": 0, "HMI_VALUEb": None, "PI_VALUEf": 0.12, "PI_VALUEb": False, "HMI_READi": 0},
            "77": {"TAG":"PI_Future_7", "HMI_VALUEi": 0, "HMI_VALUEb": None, "PI_VALUEf": 0.12, "PI_VALUEb": False, "HMI_READi": 0},
            "78": {"TAG":"PI_Future_8", "HMI_VALUEi": 0, "HMI_VALUEb": None, "PI_VALUEf": 0.12, "PI_VALUEb": False, "HMI_READi": 0},
            "79": {"TAG":"PI_Future_9", "HMI_VALUEi": 0, "HMI_VALUEb": None, "PI_VALUEf": 0.12, "PI_VALUEb": False, "HMI_READi": 0},
            "80": {"TAG":"PI_Future_10", "HMI_VALUEi": 0, "HMI_VALUEb": None, "PI_VALUEf": 0.12, "PI_VALUEb": False, "HMI_READi": 0}
        }
        # define initial dictionary. save upon run 1 time,
        JsonWriter(HMItoPIDict, "PiHmiDict.json")

    else:
        HMItoPIDict = JsonReader("PiHmiDict.json")

    while True:
        #data = HMItoPIDict
        # Go through dictonary and see what HMI updated and get that values
        for index in range(1, 50):
            DictTemp = HMItoPIDict.get(str(index), "Not Found")
            for value in DictIterator(DictTemp, v):
                DictLine.append(value)
            if DictLine[5] == 1:   # HMI new value
                Index = index
                HMIValuei = DictLine[1]
                HMIValueb = DictLine[2]

                #********************************************************
                match (Index):          #   '0' is not in list, so will pass. those reater than 49 will be passed also
                    case 1:                         # integer
                        RHT_HMI = HMIValuei      # JSON sends INTEGER value
                        print('HMI Sent for index # ',Index, "tag ", DictLine[0], " with value of: ", str(HMIValuei))
                    case 2:                         # integer
                        HMI_TramStopTime = HMIValuei
                        print('HMI Sent for index # ', Index, "for ", DictLine[0], " with value of: ", str(HMIValuei))
                    case 3:
                        HMI_AllQuietb = HMIValueb
                        FromHmiPrint(DictLine[0], HMIValueb)
                    case 4:
                        HMI_LIGHTONOFFb = HMIValueb
                        FromHmiPrint(DictLine[0], HMIValueb)
                    case 5:
                        HMI_RR2_RR3Pwrb = HMIValueb
                        FromHmiPrint(DictLine[0], HMIValueb)
                    case 6:
                        HMI_RRBellb = HMIValueb
                        FromHmiPrint(DictLine[0], HMIValueb)
                    case 7:
                        HMI_RRDieselSteamb = HMIValueb
                        FromHmiPrint(DictLine[0], HMIValueb)
                    case 8:
                        HMI_RRHornb = HMIValueb
                        FromHmiPrint(DictLine[0], HMIValueb)
                    case 9:
                        HMI_RRQuietb = HMIValueb
                        FromHmiPrint(DictLine[0], HMIValueb)
                    case 10:
                        HMI_RRWhistleb = HMIValueb
                        FromHmiPrint(DictLine[0], HMIValueb)
                    case 11:
                        HMI_Switch1ABb = HMIValueb
                        FromHmiPrint(DictLine[0], HMIValueb)
                    case 12:
                        HMI_Switch2RR3b = HMIValueb
                        FromHmiPrint(DictLine[0], HMIValueb)
                    case 13:
                        HMI_Switch3RR4b = HMIValueb
                        FromHmiPrint(DictLine[0], HMIValueb)
                    case 14:
                        HMI_Switch4RR3b = HMIValueb
                        FromHmiPrint(DictLine[0], HMIValueb)
                    case 15:
                        HMI_Switch5ABb = HMIValueb
                        FromHmiPrint(DictLine[0], HMIValueb)
                    case 16:
                        HMI_Switch6ABb = HMIValueb
                        FromHmiPrint(DictLine[0], HMIValueb)
                    case 17:
                        HMI_TramQuietb = HMIValueb
                        FromHmiPrint(DictLine[0], HMIValueb)
                    case 18:
                        HMI_TramStpStn_2b = HMIValueb
                        FromHmiPrint(DictLine[0], HMIValueb)
                    case 19:
                        HMI_TramStpStn_3b = HMIValueb
                        FromHmiPrint(DictLine[0], HMIValueb)
                    case 20:
                        HMI_TramStpStn_5b = HMIValueb
                        FromHmiPrint(DictLine[0], HMIValueb)
                    case 21:
                        HMI_TramStpStn_6b = HMIValueb
                        FromHmiPrint(DictLine[0], HMIValueb)
                    case 22:
                        pass    #   future inputs to 49
                #*******************************************************

                #-----Update & save new line to dictionary clearing HMI values--------------
                PIupdate = {
                    str(index): {"TAG": DictLine[0], "HMI_VALUEb": None, "HMI_VALUEi": 0, "PI_VALUEf": 0.123, "PI_VALUEb": None, "HMI_READi": 0}
                }

                HMItoPIDict.update(PIupdate)
                DictLine = []
            DictLine = []          # clear list for next line read
        # *********************change values in HMI ***********************************
        HmiPi = input("Change HMI value, y = HMI, anykey = PI changes: ")
        if HmiPi == 'y' or HmiPi == 'Y':
            zz = int(input("Enter INDEX number, default = 1: "))

            if zz < 1 or zz > 21: zz = 1
            DictTemp = (HMItoPIDict.get(str(zz)))
            for value in DictIterator(DictTemp, v):
                DictLine.append(value) #getting values
            HMIValuei = DictLine[1]  #for disply
            HMIValueb = DictLine[2]  #for display
            if zz < 3:
                print("you selected ",DictLine[0], " with a value of ", str(HMIValuei))
                HMIValuei = input("Enter new value ")
            if zz > 2:
                print("you selected ",DictLine[0], " with a value of ", str(HMIValueb))
                zz2b = input("Hit Enter to NOT: ")
                HMIValueb = not(HMIValueb)
            PIupdate = {
                str(zz): {"TAG": int(HMIValuei), "HMI_VALUEb": HMIValueb, "HMI_VALUEi": DictLine[1], "PI_VALUEf": 0, "PI_VALUEb": None, "HMI_READi": 1}
            }
            HMItoPIDict.update(PIupdate)
            DictLine = []
        # *************************change PI values for HMI***************************

        x = input("do you want to change PI values? y or anykey: ")
        if x == 'y' or x == 'Y':
            OPIndexi = 53
            OPIndex = input("Input PI INDEX to change. Default is 53. Range 50 to 70:  ")
            if OPIndex == "" or int(OPIndex) < 50 or int(OPIndex) > 70: OpIndexi = 53
            else: OPIndexi = int(OPIndex)
            DictTemp = (HMItoPIDict.get(str(OPIndexi)))
            print("B4 Chng: ", HMItoPIDict.get(str(OPIndexi), "Not Found"))
            for value in DictIterator(DictTemp, v):
                DictLine.append(value) #getting values
            PIValuef = DictLine[3]  #for disply
            PIValueb = DictLine[4]  #for display
            if OPIndexi >= 50 and OPIndexi <= 52:
                print("present value:", str(DictLine[3]))
                OpValuef = float(input("enter new float value: "))
                PIupdate = {
                    str(OPIndexi): {"TAG": DictLine[0], "HMI_VALUEb": None, "HMI_VALUEi": 0, "PI_VALUEf": OpValuef, "PI_VALUEb": None, "HMI_READi": 2}
                }
                HMItoPIDict.update(PIupdate)
            else:
                y = "present value:", str(DictLine[4])
                print("present value:", str(DictLine[4]))
                OpValue = input(" hit enter to NOT")
                x = not(bool(DictLine[4]))
                print("New Value for INDEX #", str(OPIndexi), " : ", x)
                PIupdate = {
                    str(OPIndexi): {"TAG": DictLine[0], "HMI_VALUEb": None, "HMI_VALUEi": 0, "PI_VALUEf": 0.123, "PI_VALUEb": x, "HMI_READi": 2}
                }
                HMItoPIDict.update(PIupdate)
            DictLine = []
            print(HMItoPIDict.get(OPIndexi))
        x = input("do you want to print dictionary? 'y' = print or anykey = no:")
        if x =='y' or x == 'Y':
            print("New Dictionary")
            print(HMItoPIDict)
        z = input("save dictionary to disk? 'y' or anykey: ")
        if z == 'y' or z == 'Y': JsonWriter(HMItoPIDict, "PiHmiDict.json")
        x = input("Do you want to load new dictionary? 'y' or anykey use existing: ")
        if x == 'y' or x == "Y":
            # HMItoPIDict = JsonWriter(HMItoPIDict, "PiHmiDict.json")
            HMItoPIDict = JsonReader("PiHmiDict.json")
