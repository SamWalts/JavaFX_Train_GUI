package org.example;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;


public class JsonTestMain {

    private String dadTest1 = "{\"1\":{\"TAG\":\"HMI_RHT\",\"HMI_VALUEi\":123,\"HMI_VALUEb\":false,\"PI_VALUEf\":0.0,\"PI_VALUEb\":null,\"HMI_READi\":1},\"2\":{\"TAG\":\"HMI_TramStopTime\",\"HMI_VALUEi\":10,\"HMI_VALUEb\":true,\"PI_VALUEf\":0.0,\"PI_VALUEb\":null,\"HMI_READi\":0}}";

    public static void main(String[] args) {
        JsonTestMain main = new JsonTestMain();
        ObjectMapper objectMapper = new ObjectMapper();
        try {
            // Deserialize the JSON string into a JsonNode
            JsonNode rootNode = objectMapper.readTree(main.dadTest1);

            // Access the "2" part and print it
            JsonNode node2 = rootNode.get("1").get("HMI_VALUEi");
            System.out.println("HMI_VALUEi of 1 is: " + node2);

        } catch (Exception e) {
            e.printStackTrace();
        }
    }
}