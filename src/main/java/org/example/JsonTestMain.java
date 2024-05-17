package org.example;

import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.ObjectMapper;
import java.io.File;
import java.io.IOException;
import java.util.List;
import java.util.Map;
import java.util.HashMap;

public class JsonTestMain {

    private static final String FILE_PATH = "PiHmiDict.json";

    public static void main(String[] args) {
        try {
            // Deserialize the JSON file into a list of maps
            List<Map<String, Object>> dataList = readDataListFromFile(FILE_PATH);

            // Process each map in the list
            for (Map<String, Object> dataMap : dataList) {
                // Copy the map to workMap
                Map<String, Object> workMap = new HashMap<>(dataMap);

                // Process the data map
                processDataMap(dataMap, "5");
                updateValueInMap(dataMap, "4", "HMI_VALUEi", 33);
                processDataMap(dataMap, "4");

                // Compare and set HMI_READi
                compareAndSetHMI_READi(dataMap, workMap);
            }
        } catch (IOException e) {
            throw new RuntimeException(e);
        }
    }

    private static List<Map<String, Object>> readDataListFromFile(String filePath) throws IOException {
        ObjectMapper objectMapper = new ObjectMapper();
        return objectMapper.readValue(new File(filePath), new TypeReference<List<Map<String, Object>>>() {});
    }

    private static void processDataMap(Map<String, Object> dataMap, String mapKey) {
        // Access specific values within the map
        var nestedValue = dataMap.get(mapKey);
        System.out.println(nestedValue);
        if (nestedValue != null && nestedValue instanceof Map) {
            Map<String, Object> valueMap = (Map<String, Object>) nestedValue;
            String tagValue = (String) valueMap.get("TAG");
            System.out.println("Value of TAG in " + mapKey + " is: " + tagValue);
        }

        // Iterate through the map and print key-value pairs
        for (Map.Entry<String, Object> entry : dataMap.entrySet()) {
            System.out.println("Key: " + entry.getKey() + ", Value: " + entry.getValue());
        }
    }

    private static void updateValueInMap(Map<String, Object> dataMap, String mapKey, String variableName, Object newValue) {
        // Get the nested map corresponding to the mapKey
        Map<String, Object> nestedMap = (Map<String, Object>) dataMap.get(mapKey);

        // Check if the nested map exists
        if (nestedMap != null) {
            // Update the value in the nested map
            nestedMap.put(variableName, newValue);
            System.out.println("This is changed variable " + variableName + " " + newValue);
        } else {
            throw new RuntimeException("Nested map with key '" + mapKey + "' does not exist.");
        }
    }

    private static void compareAndSetHMI_READi(Map<String, Object> dataMap, Map<String, Object> workMap) {
        for (Map.Entry<String, Object> entry : dataMap.entrySet()) {
            if (entry.getValue() instanceof Map) {
                Map<String, Object> nestedMap = (Map<String, Object>) entry.getValue();

                // Check if HMI_READi has changed
                Object dataHmiReadi = nestedMap.get("HMI_READi");
                Object workHmiReadi = ((Map<String, Object>) workMap.get(entry.getKey())).get("HMI_READi");

                if (dataHmiReadi != null && workHmiReadi != null && !dataHmiReadi.equals(workHmiReadi)) {
                    // Update HMI_READi to 0
                    nestedMap.put("HMI_READi", 0);
                    System.out.println("HMI_READi updated to 0 for " + entry.getKey());
                }
            }
        }
    }
}
