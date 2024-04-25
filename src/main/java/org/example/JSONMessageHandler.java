package org.example;
import java.io.FileNotFoundException;
import java.io.FileReader;
import java.io.IOException;
import java.io.Reader;
import java.net.PasswordAuthentication;
import java.util.Scanner;
import java.util.Iterator;

import org.json.simple.JSONObject;
import org.json.simple.JSONArray;
import org.json.simple.parser.JSONParser;
import org.json.simple.parser.ParseException;


//public class JSONMessageHandler {
//    void handleInput(JSONArray list)
//    {
//        System.out.println(
//                "handleInput():  got a JSONArray (list) containing " +
//                        list.size() + " elements");
//
//        for (Object o : list)
//            System.out.println(o);
//    }
//
//    void handleInput(JSONObject map)
//    {
//        System.out.println(
//                "handleInput():  got a JSONObject (map) containing " +
//                        map.size() + " items");
//
//        for (Iterator it = map.keySet().iterator(); it.hasNext();)
//        {
//            Object key = it.next();
//            System.out.println(key + ": " + map.get(key));
//        }
//    }
//}



class Hi {
    public static void main(String[] args) throws ParseException, IOException, FileNotFoundException {
        JSONParser parser = new JSONParser();
        try {
            Reader reader = new FileReader("PiHmiDict.json");
            Object obj = parser.parse(reader);
            JSONObject jsonObject = (JSONObject) obj;


            for (Object key : jsonObject.keySet()) {
                String keyStr = (String) key;
                JSONObject value = (JSONObject) jsonObject.get(keyStr);
                System.out.println("Key: " + keyStr);
                System.out.println("TAG: " + value.get("TAG"));
                System.out.println("HMI_VALUEi: " + value.get("HMI_VALUEi"));
                System.out.println("HMI_VALUEb: " + value.get("HMI_VALUEb"));
                System.out.println("PI_VALUEf: " + value.get("PI_VALUEf"));
                System.out.println("PI_VALUEb: " + value.get("PI_VALUEb"));
                System.out.println("HMI_READi: " + value.get("HMI_READi"));
                System.out.println();
            }
        } catch (IOException | ParseException e) {
            e.printStackTrace();
        }
    }
}

//There are a few options here:
//
//    Use str() or repr() to convert the list to a string representation. then parse the string in Java.
//    Split the list into separate lines and write each to the Java sub process, which puts them back together into a list.
//    Use JSON. Send a JSON string of the list to Java and decode it with one of the many JSON libraries available.
//
//I'd opt for the third option, JSON, because this gives more flexibility with the types of data structures that can be communicated. e.g. you might later find yourself wanting to transfer a Python dictionary. You might also later find that you want your Java application to send a reply, and JSON can be used here too.
//
//Python to send the list as a JSON string:
//
//import json
//import subprocess
//
//# send a Python list...
//p = subprocess.Popen("java -jar "hi.jar", stdin=subprocess.PIPE, stdout=subprocess.PIPE)
//o, e = p.communicate(json.dumps(["haha", "hehe"]))
//
//>>> print o
//handleInput():  got a JSONArray (list) containing 2 elements
//haha
//hehe
//
//# send a Python dictionary...
//p = subprocess.Popen("java -jar "hi.jar", stdin=subprocess.PIPE, stdout=subprocess.PIPE)
//o, e = p.communicate(json.dumps({"hee": "haw", "blah": "blah"}))
//>>> print o
//handleInput():  got a JSONObject (map) containing 2 items
//hee: haw
//blah: blah
//
//And sample Java code to receive and parse the JSON. It can handle basic lists and dictionaries. This uses the json-simple package for the parsing:
//
//import java.util.Scanner;
//import java.util.Iterator;
//
//import org.json.simple.JSONObject;
//import org.json.simple.JSONArray;
//import org.json.simple.parser.JSONParser;
//import org.json.simple.parser.ParseException;
//
//
//class JSONMessageHandler {
//    void handleInput(JSONArray list)
//    {
//        System.out.println(
//                "handleInput():  got a JSONArray (list) containing " +
//                    list.size() + " elements");
//
//        for (Object o : list)
//            System.out.println(o);
//    }
//
//    void handleInput(JSONObject map)
//    {
//        System.out.println(
//                "handleInput():  got a JSONObject (map) containing " +
//                    map.size() + " items");
//
//        for (Iterator it = map.keySet().iterator(); it.hasNext();)
//        {
//            Object key = it.next();
//            System.out.println(key + ": " + map.get(key));
//        }
//    }
//}
//
//
//class Hi {
//    public static void main(String[] args) throws ParseException {
//        Scanner in = new Scanner(System.in);
//        Object obj = new JSONParser().parse(in.nextLine());
//        JSONMessageHandler msgHandler = new JSONMessageHandler();
//
//        if (obj instanceof JSONArray)
//            msgHandler.handleInput((JSONArray)obj);
//        else if (obj instanceof JSONObject)
//            msgHandler.handleInput((JSONObject)obj);
//    }
//}
//

