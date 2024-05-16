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


import java.io.File;
import java.io.IOException;
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

    private static final String FILE_PATH = "PiHmiDict.json";

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
    void dadTestSerializerFirstRow() throws IOException {
        // Ensure the JSON node is not null
        JsonNode jsonNode = JSON.parse(String.valueOf(new File(FILE_PATH)));

        JsonNode item1 = jsonNode.get("1");

//        assertEquals(, items.size());

        // Get the HmiToPi object for key "1" from the map and assert its properties
        JsonNode hmiToPi1 = item1.get("TAG");
        // Check the first line is not null
        assertNotNull(hmiToPi1);
        assertNotNull(item1.get("HMI_VALUEi"));
//        Work on getting this to work. Likely use JSONAssert library
//        assertThat(hmiToPi1, "HMI_RHT");

//        Convert the jsonNode to string, so we can check it. First have to get the
//        https://stackoverflow.com/questions/2525042/

        assertEquals(6, item1.size());

    }

    // TODO: Make this test one that will change the map, serialize it, then check that object
//    @Test
//    void dadTestSerializer1() throws JsonProcessingException {
//        // Ensure the JSON node is not null
//        HmiToPiList hmiToPiList = (HmiToPiList) JSON.fromJsonArray(dadTest1, HmiToPiList.class);
//        Map<String, HmiToPi> items = hmiToPiList.getItems();
//
//        // Assert the size of the map
//        assertEquals(2, hmiToPiList.getSize());
//
//        // You can access individual items from the map if needed
//        HmiToPi firstItem = items.get("1");
//        HmiToPi secondItem = items.get("2");

//        // Add assertions for individual items if needed
//        assertEquals("HMI_RHT", firstItem.getTAG());
//        assertEquals(123, firstItem.getHMI_VALUEi());
//        assertEquals(false, firstItem.isHMI_VALUEb());
//        assertEquals("HMI_TramStopTime", secondItem.getTAG());
//        assertEquals(10, secondItem.getHMI_VALUEi());
//        assertEquals(true, secondItem.isHMI_VALUEb());
//    }

//    TODO: Add test to compare maps.

//    TODO: Test to check if map is changed, then to change the Hmi_Readi to the correct value.

//    TODO: test method if map is read that is different, will pull the var, AND change the Hmi_readi to correct value
}

