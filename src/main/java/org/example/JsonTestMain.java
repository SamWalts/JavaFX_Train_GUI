package org.example;

import org.example.json.JSON;
import org.example.pojo.HmiData;

import java.io.IOException;
import java.util.HashMap;
import java.util.Map;

public class JsonTestMain {

//    Read from here. This is the exact same that dad sends
    private static final String FILE_PATH = "PiHmiDict.json";
//    This will be the one I change to TEST
    private static final String FILE_PATH_CHANGE = "PiHmiDictCHANGED.json";

    public static void main(String[] args) {
        try {
            // Deserialize the JSON file into a map of HmiData objects
            Map<String, HmiData> hmiDataMap = JSON.readHmiDataMapFromFile(FILE_PATH);

            // Create a work map to track original values for comparison
            Map<String, HmiData> workMap = new HashMap<>(hmiDataMap);

            // Compare and set HMI_READi
            JSON.compareAndSetHMI_READi(hmiDataMap, workMap);
        } catch (IOException e) {
            throw new RuntimeException(e);
        }
    }

    private static void processData(HmiData data) {
        // Access and print specific values within the HmiData object
        System.out.println(data);
        String tagValue = data.getTag();
        System.out.println("Value of TAG is: " + tagValue);
    }

    private static void updateValue(HmiData data, String variableName, Object newValue) {
//      This needs to get changed no matter what
        if (variableName.equals("HMI_READi")) {
            data.setHmiReadi(2);
        }
        switch (variableName) {
            case "HMI_VALUEi":
                data.setHmiValuei((Integer) newValue);
                data.setHmiReadi((2));
                break;
            case "HMI_VALUEb":
                data.setHmiValueb((Boolean) newValue);
                data.setHmiReadi((2));
                break;
            case "PI_VALUEf":
                data.setPiValuef((Float) newValue);
                data.setHmiReadi((2));
                break;
            case "PI_VALUEb":
                data.setPiValueb((Boolean) newValue);
                data.setHmiReadi((2));
                break;
            default:
                throw new IllegalArgumentException("Unknown variable name: " + variableName);
        }
        System.out.println("Updated " + variableName + " to " + newValue);
    }
}
