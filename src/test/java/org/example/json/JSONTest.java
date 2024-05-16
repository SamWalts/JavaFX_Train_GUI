package org.example.json;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.JsonNode;
import org.example.json.pojo.DayPOJO;
import org.example.json.pojo.HmiToPi;
import org.example.json.pojo.HmiToPiList;
import org.example.json.pojo.SimpleTestCasePOJOJson;
import org.junit.jupiter.api.Test;
import org.hamcrest.MatcherAssert.*;


import java.util.List;
import java.util.Map;

import static org.hamcrest.MatcherAssert.assertThat;
import static org.hamcrest.Matchers.*;
import static org.junit.jupiter.api.Assertions.*;

class JSONTest {

    private String simpleTest = "{\n" +
            "  \"test\"  :  \"Working\",\n" +
            "  \"author\": \"Rui\"\n" +
            "}";

    private String dayScenario1 = "{\n" +
            "  \"date\": \"2019-12-25\",\n" +
            "  \"name\": \"Christmas Day\"\n" +
            "}";

    private String dadTest1 = "[{\"1\":{\"TAG\":\"HMI_RHT\",\"HMI_VALUEi\":123,\"HMI_VALUEb\":false,\"PI_VALUEf\":0.0,\"PI_VALUEb\":null,\"HMI_READi\":1},\"2\":{\"TAG\":\"HMI_TramStopTime\",\"HMI_VALUEi\":10,\"HMI_VALUEb\":true,\"PI_VALUEf\":0.0,\"PI_VALUEb\":null,\"HMI_READi\":0}}]";
    @Test
    void parse() throws JsonProcessingException {
        JsonNode node = JSON.parse(simpleTest);

        assertEquals(node.get("test").asText(), "Working");
    }

    @Test
    void fromJson() throws JsonProcessingException {
        JsonNode node = JSON.parse(simpleTest);
        SimpleTestCasePOJOJson pojo = JSON.fromJson(node, SimpleTestCasePOJOJson.class);

        assertEquals(pojo.getTest(), "Working");
    }

    @Test
    void toJson() {
        SimpleTestCasePOJOJson pojo = new SimpleTestCasePOJOJson();
        pojo.setTest("Testing 123");

        JsonNode node = JSON.toJson(pojo);
        assertEquals(node.get("test").asText(), "Testing 123");
    }

    @Test
    void stringifyJson() throws JsonProcessingException {
        SimpleTestCasePOJOJson pojo = new SimpleTestCasePOJOJson();
        pojo.setTest("Testing 123");

        JsonNode node = JSON.toJson(pojo);

        System.out.println(JSON.stringifyJson(node));
        System.out.println(JSON.prettyPrint(node));
    }

    @Test
    void dayTestScenario1() throws JsonProcessingException {
        JsonNode node = JSON.parse(dayScenario1);
        DayPOJO pojo = JSON.fromJson(node, DayPOJO.class);

        assertThat(pojo.getDate().toString(), containsString("Dec 24"));
    }

//    @Test
//    void dadToJson() {
//        String dadTest11 = dadTest1;
//        HmiToPiList[] pojo = new HmiToPiList[](dadTest11);
//        pojo.setTest("Testing 123");
//
//        JsonNode node = JSON.toJson(pojo);
//        assertEquals(node.get("test").asText(), "Testing 123");
//    }


    @Test
    void dadTestSerializer() throws JsonProcessingException {
        // Ensure the JSON node is not null
        JsonNode jsonNode = JSON.parse(dadTest1);

        // Deserialize the JSON into an HmiToPiList object
        HmiToPiList hmiToPiList = JSON.fromJson(jsonNode, HmiToPiList.class);

        // Get the map of items from the HmiToPiList object
        Map<String, HmiToPi> items = hmiToPiList.getItems();

        // Assert the size of the map
        assertEquals(2, items.size());

        // Get the HmiToPi object for key "1" from the map and assert its properties
        HmiToPi hmiToPi1 = items.get("1");
        assertEquals("HMI_RHT", hmiToPi1.getTag());
        assertEquals(123, hmiToPi1.getHmiValuei());
        assertEquals(false, hmiToPi1.getPiValueb());

        // Get the HmiToPi object for key "2" from the map and assert its properties
        HmiToPi hmiToPi2 = items.get("2");
        assertEquals("HMI_TramStopTime", hmiToPi2.getTag());
        assertEquals(10, hmiToPi2.getHmiValuei());
        assertEquals(true, hmiToPi2.getPiValueb());

        // You can add more assertions here if needed
    }
    @Test
    void dadTestSerializer1() throws JsonProcessingException {
        // Ensure the JSON node is not null
        HmiToPiList hmiToPiList = (HmiToPiList) JSON.fromJsonArray(dadTest1, HmiToPiList.class);
        Map<String, HmiToPi> items = hmiToPiList.getItems();

        // Assert the size of the map
        assertEquals(2, hmiToPiList.getSize());

        // You can access individual items from the map if needed
//        HmiToPi firstItem = items.get("1");
//        HmiToPi secondItem = items.get("2");

//        // Add assertions for individual items if needed
//        assertEquals("HMI_RHT", firstItem.getTAG());
//        assertEquals(123, firstItem.getHMI_VALUEi());
//        assertEquals(false, firstItem.isHMI_VALUEb());
//        assertEquals("HMI_TramStopTime", secondItem.getTAG());
//        assertEquals(10, secondItem.getHMI_VALUEi());
//        assertEquals(true, secondItem.isHMI_VALUEb());
    }
}

