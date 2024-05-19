package org.example.json;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.*;
import org.example.pojo.HmiData;

import java.io.File;
import java.io.IOException;
import java.util.Map;

public class JSON {
    private static ObjectMapper objectMapper = getDefaultObjectMapper();

    private static ObjectMapper getDefaultObjectMapper() {
        ObjectMapper defaultObjectMapper = new ObjectMapper();
        defaultObjectMapper.configure(DeserializationFeature.FAIL_ON_UNKNOWN_PROPERTIES, false);
        return defaultObjectMapper;
    }

    private static String generateString(JsonNode node, boolean pretty) throws JsonProcessingException {
        ObjectWriter objectWriter = objectMapper.writer();
        if ( pretty )
            objectWriter = objectWriter.with(SerializationFeature.INDENT_OUTPUT);
        return objectWriter.writeValueAsString(node);
    }

    public static Map<String, HmiData> readHmiDataMapFromFile(String filePath) throws IOException {
        return objectMapper.readValue(new File(filePath), new TypeReference<Map<String, HmiData>>() {});
    }

//    Maybe change this to be read into a new map, which as of now can be tested by sending it into a new file, and ensuring the change is correct
//    OR, it can be kept the same,
    public static void updateValue(HmiData data, String variableName, Object newValue) {
//      If the JAVA program changes something, then HMI_READi MUST be set to 1 for the Python program to know a change was made
        if (variableName.equals("HMI_READi")) {
            data.setHmiReadi(1);
        }
        switch (variableName) {
            case "HMI_VALUEi":
                data.setHmiValuei((Integer) newValue);
                data.setHmiReadi((1));
                break;
            case "HMI_VALUEb":
                data.setHmiValueb((Boolean) newValue);
                data.setHmiReadi((1));
                break;
            case "PI_VALUEf":
                data.setPiValuef((Float) newValue);
                data.setHmiReadi((1));
                break;
            case "PI_VALUEb":
                data.setPiValueb((Boolean) newValue);
                data.setHmiReadi((1));
                break;
            default:
                throw new IllegalArgumentException("Unknown variable name: " + variableName);
        }

    }

    public static void compareAndSetHMI_READi(Map<String, HmiData> hmiDataMap, Map<String, HmiData> workMap) {
        for (Map.Entry<String, HmiData> entry : hmiDataMap.entrySet()) {
            HmiData data = entry.getValue();
            HmiData originalData = workMap.get(entry.getKey());
            if (originalData != null && !data.getHmiReadi().equals(originalData.getHmiReadi())) {
                data.setHmiReadi(0);
                System.out.println("HMI_READi updated to 0 for " + data.getTag());
            }
        }
    }

    public static void writeMapToFile(Map<String, ?> map, String filePath) throws IOException {
        // Configure the ObjectMapper to preserve the original structure
        objectMapper.configure(SerializationFeature.INDENT_OUTPUT, true);

        // Write the map to the file
        objectMapper.writeValue(new File(filePath), map);
    }
}
