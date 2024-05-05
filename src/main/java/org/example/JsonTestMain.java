package org.example;

import com.fasterxml.jackson.core.exc.StreamReadException;
import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.DatabindException;
import org.example.json.JSON;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import java.io.File;
import java.io.IOException;
import java.util.Map;

public class JsonTestMain {

    private String dadTest1 = "{\"1\":{\"TAG\":\"HMI_RHT\",\"HMI_VALUEi\":123,\"HMI_VALUEb\":false,\"PI_VALUEf\":0.0,\"PI_VALUEb\":null,\"HMI_READi\":1},\"2\":{\"TAG\":\"HMI_TramStopTime\",\"HMI_VALUEi\":10,\"HMI_VALUEb\":true,\"PI_VALUEf\":0.0,\"PI_VALUEb\":null,\"HMI_READi\":0}}";

    private static final String FILE_PATH = "PiHmiDict.json";

    public static void main(String[] args) {
        JsonTestMain main = new JsonTestMain();
        ObjectMapper objectMapper = new ObjectMapper();
        try {
            // Deserialize the JSON string into a JsonNode
//            JsonNode rootNode = objectMapper.readTree(main.dadTest1);
//                JsonNode rootNode = JSON.parse(main.dadTest1);
            JsonNode rootNode = JSON.parse(new File(FILE_PATH));
            // Access the "2" part and print it
//            JsonNode node2 = rootNode.get("1");
////            JsonNode node2 = rootNode.get("1").get("HMI_VALUEi");
//            System.out.println("HMI_VALUEi of 1 is: " + node2);
            Map<String, Object> dataMap = objectMapper.readValue(new File(FILE_PATH), new TypeReference<Map<String, Object>>() {
            });

            Object value1 = dataMap.get("1");

            if (value1 != null && value1 instanceof Map) {
                Map<String, Object> valueMap = (Map<String, Object>) value1;
                String tagValue = (String) valueMap.get("TAG");
                System.out.println("Line one TAG is: " + tagValue);
            }
            // Iterate through the map and print key-value pairs
            for (Map.Entry<String, Object> entry : dataMap.entrySet()) {
                System.out.println("Key: " + entry.getKey() + ", Value: " + entry.getValue());
            }
        } catch (StreamReadException | DatabindException e) {
            throw new RuntimeException(e);
        } catch (IOException e) {
            throw new RuntimeException(e);
        }
    }
}