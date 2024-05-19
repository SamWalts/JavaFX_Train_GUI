package org.example.json;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.JsonNode;
import org.example.JsonTestMain;
import org.example.pojo.HmiData;
import org.junit.jupiter.api.Test;

import java.io.File;
import java.io.IOException;
import java.util.Map;

import static org.hamcrest.MatcherAssert.assertThat;
import static org.hamcrest.Matchers.*;
import static org.junit.jupiter.api.Assertions.*;

class JSONTest {

    private static final String FILE_PATH = "PiHmiDict.json";
    private static final String TEST_FILE_PATH_CHANGE = "testFileCHANGED.json";

    @Test
    void testReadHmiDataMapFromFile() throws IOException {
        Map<String, HmiData> hmiDataMap = JSON.readHmiDataMapFromFile(FILE_PATH);

        // Basic assertions to ensure the file was read and parsed correctly
        assertNotNull(hmiDataMap);
        assertFalse(hmiDataMap.isEmpty());

        // Verify specific entries
        assertThat(hmiDataMap, hasKey("1"));
        assertThat(hmiDataMap, hasKey("2"));

        HmiData data1 = hmiDataMap.get("1");
        assertEquals("HMI_RHT", data1.getTag());
        assertEquals(0, data1.getHmiValuei());
        assertEquals(0.123f, data1.getPiValuef());
    }

//    Check some random ones to see if the TAG values have changed.
    @Test
    void testProcessData() throws IOException {
        Map<String, HmiData> hmiDataMap = JSON.readHmiDataMapFromFile(FILE_PATH);
        HmiData data1 = hmiDataMap.get("1");
        HmiData data14 = hmiDataMap.get("14");

        assertEquals("HMI_RHT", data1.getTag());
        assertEquals("HMI_Switch4RR3b", data14.getTag());
    }

//    Change a variable and check if it also has changed the HMI_READi variable. IF JAVA changes this then the variable must be set to 1
    @Test
    void testUpdateValue() throws IOException {
        Map<String, HmiData> hmiDataMap = JSON.readHmiDataMapFromFile(FILE_PATH);
        HmiData data1 = hmiDataMap.get("1");

        JSON.updateValue(data1, "HMI_VALUEi", 33);

        assertEquals(33, data1.getHmiValuei());
        assertEquals(1, data1.getHmiReadi());
    }

//    Make sure that the value changes, then print it into the new file and check if it saved correctly
    @Test
    void testUpdateFile() throws IOException {
        Map<String, HmiData> hmiDataMap = JSON.readHmiDataMapFromFile(FILE_PATH);
        HmiData data1 = hmiDataMap.get("1");

        JSON.updateValue(data1, "HMI_VALUEi", 44);

        assertEquals(44, data1.getHmiValuei());
        assertEquals(1, data1.getHmiReadi());
//      Print the map onto the new file.
        JSON.writeMapToFile(hmiDataMap, TEST_FILE_PATH_CHANGE);

//      Get the new un serialized data from it
        Map<String, HmiData> newDataMap = JSON.readHmiDataMapFromFile(TEST_FILE_PATH_CHANGE);
        HmiData dataNew1 = newDataMap.get("1");

//        Check if it is the correct value
        assertEquals(44, dataNew1.getHmiValuei());
    }

    @Test
    void testCompareAndSetHMI_READi() throws IOException {
        Map<String, HmiData> hmiDataMap = JSON.readHmiDataMapFromFile(FILE_PATH);
        Map<String, HmiData> workMap = JSON.readHmiDataMapFromFile(FILE_PATH);

        // Update a value to trigger the comparison
        hmiDataMap.get("1").setHmiReadi(1);

        JSON.compareAndSetHMI_READi(hmiDataMap, workMap);

        assertEquals(0, hmiDataMap.get("1").getHmiReadi());
    }
}
