package org.example.jsonOperator;

import org.example.jsonOperator.dao.HMIJSONDAOStub;
import org.example.jsonOperator.dto.HmiData;
import org.example.jsonOperator.service.JSONOperatorServiceStub;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

import java.io.IOException;
import java.util.HashMap;
import java.util.Map;

import static org.hamcrest.MatcherAssert.assertThat;
import static org.hamcrest.Matchers.*;
import static org.junit.jupiter.api.Assertions.*;

class JSONServiceTests {

    private final String FILE_PATH = "PiHmiDict.json";
    private final String TEST_FILE_PATH_CHANGE = "testFileCHANGED.json";
    private final String TEST_SERVER_STRING_FULL = "[{\"INDEX\":1,\"TAG\":\"HMI_RHT\",\"HMI_VALUEb\":false,\"HMI_VALUEi\":25,\"PI_VALUEf\":0.0,\"PI_VALUEb\":null,\"HMI_READi\":1},{\"INDEX\":2,\"TAG\":\"HMI_TramStopTime\",\"HMI_VALUEb\":true,\"HMI_VALUEi\":10,\"PI_VALUEf\":0.0,\"PI_VALUEb\":null,\"HMI_READi\":0},{\"INDEX\":3,\"TAG\":\"HMI_AllQuietb\",\"HMI_VALUEb\":false,\"HMI_VALUEi\":0,\"PI_VALUEf\":0.0,\"PI_VALUEb\":null,\"HMI_READi\":1},{\"INDEX\":4,\"TAG\":\"HMI_LIGHTONOFFb\",\"HMI_VALUEb\":true,\"HMI_VALUEi\":0,\"PI_VALUEf\":0.0,\"PI_VALUEb\":null,\"HMI_READi\":0},{\"INDEX\":5,\"TAG\":\"HMI_RR2_RR3Pwrb\",\"HMI_VALUEb\":false,\"HMI_VALUEi\":0,\"PI_VALUEf\":0.0,\"PI_VALUEb\":null,\"HMI_READi\":1},{\"INDEX\":6,\"TAG\":\"HMI_RRBellb\",\"HMI_VALUEb\":true,\"HMI_VALUEi\":0,\"PI_VALUEf\":0.0,\"PI_VALUEb\":null,\"HMI_READi\":0},{\"INDEX\":7,\"TAG\":\"HMI_RRDieselSteamb\",\"HMI_VALUEb\":false,\"HMI_VALUEi\":0,\"PI_VALUEf\":0.0,\"PI_VALUEb\":null,\"HMI_READi\":0},{\"INDEX\":8,\"TAG\":\"HMI_RRHornb\",\"HMI_VALUEb\":true,\"HMI_VALUEi\":0,\"PI_VALUEf\":0.0,\"PI_VALUEb\":null,\"HMI_READi\":0},{\"INDEX\":9,\"TAG\":\"HMI_RRQuietb\",\"HMI_VALUEb\":false,\"HMI_VALUEi\":0,\"PI_VALUEf\":0.0,\"PI_VALUEb\":null,\"HMI_READi\":2},{\"INDEX\":10,\"TAG\":\"HMI_RRWhistleb\",\"HMI_VALUEb\":true,\"HMI_VALUEi\":0,\"PI_VALUEf\":0.0,\"PI_VALUEb\":null,\"HMI_READi\":2},{\"INDEX\":11,\"TAG\":\"HMI_Switch1ABb\",\"HMI_VALUEb\":true,\"HMI_VALUEi\":0,\"PI_VALUEf\":0.0,\"PI_VALUEb\":null,\"HMI_READi\":2},{\"INDEX\":12,\"TAG\":\"HMI_Switch2RR3b\",\"HMI_VALUEb\":true,\"HMI_VALUEi\":0,\"PI_VALUEf\":0.0,\"PI_VALUEb\":null,\"HMI_READi\":2},{\"INDEX\":13,\"TAG\":\"HMI_Switch3RR4b\",\"HMI_VALUEb\":false,\"HMI_VALUEi\":0,\"PI_VALUEf\":0.0,\"PI_VALUEb\":null,\"HMI_READi\":0},{\"INDEX\":14,\"TAG\":\"HMI_Switch4RR3b\",\"HMI_VALUEb\":true,\"HMI_VALUEi\":0,\"PI_VALUEf\":0.0,\"PI_VALUEb\":null,\"HMI_READi\":0},{\"INDEX\":15,\"TAG\":\"HMI_Switch5ABb\",\"HMI_VALUEb\":false,\"HMI_VALUEi\":0,\"PI_VALUEf\":0.0,\"PI_VALUEb\":null,\"HMI_READi\":0},{\"INDEX\":16,\"TAG\":\"HMI_Switch6ABb\",\"HMI_VALUEb\":true,\"HMI_VALUEi\":0,\"PI_VALUEf\":0.0,\"PI_VALUEb\":null,\"HMI_READi\":0},{\"INDEX\":17,\"TAG\":\"HMI_TramQuietb\",\"HMI_VALUEb\":true,\"HMI_VALUEi\":0,\"PI_VALUEf\":0.0,\"PI_VALUEb\":null,\"HMI_READi\":0},{\"INDEX\":18,\"TAG\":\"HMI_TramStpStn_2b\",\"HMI_VALUEb\":true,\"HMI_VALUEi\":0,\"PI_VALUEf\":0.0,\"PI_VALUEb\":null,\"HMI_READi\":0},{\"INDEX\":19,\"TAG\":\"HMI_TramStpStn_3b\",\"HMI_VALUEb\":false,\"HMI_VALUEi\":0,\"PI_VALUEf\":0.0,\"PI_VALUEb\":null,\"HMI_READi\":0},{\"INDEX\":20,\"TAG\":\"HMI_TramStpStn_5b\",\"HMI_VALUEb\":true,\"HMI_VALUEi\":0,\"PI_VALUEf\":0.0,\"PI_VALUEb\":null,\"HMI_READi\":0},{\"INDEX\":21,\"TAG\":\"HMI_TramStpStn_6b\",\"HMI_VALUEb\":false,\"HMI_VALUEi\":0,\"PI_VALUEf\":0.0,\"PI_VALUEb\":null,\"HMI_READi\":0},{\"INDEX\":22,\"TAG\":\"HMI_Future_1\",\"HMI_VALUEb\":true,\"HMI_VALUEi\":0,\"PI_VALUEf\":0.0,\"PI_VALUEb\":null,\"HMI_READi\":0},{\"INDEX\":23,\"TAG\":\"HMI_Future_2\",\"HMI_VALUEb\":true,\"HMI_VALUEi\":0,\"PI_VALUEf\":0.0,\"PI_VALUEb\":null,\"HMI_READi\":0},{\"INDEX\":24,\"TAG\":\"HMI_Future_3\",\"HMI_VALUEb\":true,\"HMI_VALUEi\":0,\"PI_VALUEf\":0.0,\"PI_VALUEb\":null,\"HMI_READi\":0},{\"INDEX\":25,\"TAG\":\"HMI_Future_4\",\"HMI_VALUEb\":true,\"HMI_VALUEi\":0,\"PI_VALUEf\":0.0,\"PI_VALUEb\":null,\"HMI_READi\":0},{\"INDEX\":26,\"TAG\":\"HMI_Future_5\",\"HMI_VALUEb\":true,\"HMI_VALUEi\":0,\"PI_VALUEf\":0.0,\"PI_VALUEb\":null,\"HMI_READi\":0},{\"INDEX\":27,\"TAG\":\"HMI_Future_6\",\"HMI_VALUEb\":true,\"HMI_VALUEi\":0,\"PI_VALUEf\":0.0,\"PI_VALUEb\":null,\"HMI_READi\":0},{\"INDEX\":28,\"TAG\":\"HMI_Future_7\",\"HMI_VALUEb\":true,\"HMI_VALUEi\":0,\"PI_VALUEf\":0.0,\"PI_VALUEb\":null,\"HMI_READi\":0},{\"INDEX\":29,\"TAG\":\"HMI_Future_8\",\"HMI_VALUEb\":true,\"HMI_VALUEi\":0,\"PI_VALUEf\":0.0,\"PI_VALUEb\":null,\"HMI_READi\":0},{\"INDEX\":30,\"TAG\":\"HMI_Future_9\",\"HMI_VALUEb\":true,\"HMI_VALUEi\":0,\"PI_VALUEf\":0.0,\"PI_VALUEb\":null,\"HMI_READi\":0},{\"INDEX\":31,\"TAG\":\"HMI_Future_10\",\"HMI_VALUEb\":true,\"HMI_VALUEi\":0,\"PI_VALUEf\":0.0,\"PI_VALUEb\":null,\"HMI_READi\":0},{\"INDEX\":32,\"TAG\":\"HMI_Future_11\",\"HMI_VALUEb\":true,\"HMI_VALUEi\":0,\"PI_VALUEf\":0.0,\"PI_VALUEb\":null,\"HMI_READi\":0},{\"INDEX\":33,\"TAG\":\"HMI_Future_12\",\"HMI_VALUEb\":true,\"HMI_VALUEi\":0,\"PI_VALUEf\":0.0,\"PI_VALUEb\":null,\"HMI_READi\":0},{\"INDEX\":34,\"TAG\":\"HMI_Future_13\",\"HMI_VALUEb\":true,\"HMI_VALUEi\":0,\"PI_VALUEf\":0.0,\"PI_VALUEb\":null,\"HMI_READi\":0},{\"INDEX\":35,\"TAG\":\"HMI_Future_14\",\"HMI_VALUEb\":true,\"HMI_VALUEi\":0,\"PI_VALUEf\":0.0,\"PI_VALUEb\":null,\"HMI_READi\":0},{\"INDEX\":36,\"TAG\":\"HMI_Future_15\",\"HMI_VALUEb\":true,\"HMI_VALUEi\":0,\"PI_VALUEf\":0.0,\"PI_VALUEb\":null,\"HMI_READi\":0},{\"INDEX\":37,\"TAG\":\"HMI_Future_16\",\"HMI_VALUEb\":true,\"HMI_VALUEi\":0,\"PI_VALUEf\":0.0,\"PI_VALUEb\":null,\"HMI_READi\":0},{\"INDEX\":38,\"TAG\":\"HMI_Future_17\",\"HMI_VALUEb\":true,\"HMI_VALUEi\":0,\"PI_VALUEf\":0.0,\"PI_VALUEb\":null,\"HMI_READi\":0},{\"INDEX\":39,\"TAG\":\"HMI_Future_18\",\"HMI_VALUEb\":true,\"HMI_VALUEi\":0,\"PI_VALUEf\":0.0,\"PI_VALUEb\":null,\"HMI_READi\":0},{\"INDEX\":40,\"TAG\":\"HMI_Future_19\",\"HMI_VALUEb\":true,\"HMI_VALUEi\":0,\"PI_VALUEf\":0.0,\"PI_VALUEb\":null,\"HMI_READi\":0},{\"INDEX\":41,\"TAG\":\"HMI_Future_20\",\"HMI_VALUEb\":true,\"HMI_VALUEi\":0,\"PI_VALUEf\":0.0,\"PI_VALUEb\":null,\"HMI_READi\":0},{\"INDEX\":42,\"TAG\":\"HMI_Future_21\",\"HMI_VALUEb\":true,\"HMI_VALUEi\":0,\"PI_VALUEf\":0.0,\"PI_VALUEb\":null,\"HMI_READi\":0},{\"INDEX\":43,\"TAG\":\"HMI_Future_22\",\"HMI_VALUEb\":true,\"HMI_VALUEi\":0,\"PI_VALUEf\":0.0,\"PI_VALUEb\":null,\"HMI_READi\":0},{\"INDEX\":44,\"TAG\":\"HMI_Future_23\",\"HMI_VALUEb\":true,\"HMI_VALUEi\":0,\"PI_VALUEf\":0.0,\"PI_VALUEb\":null,\"HMI_READi\":0},{\"INDEX\":45,\"TAG\":\"HMI_Future_24\",\"HMI_VALUEb\":true,\"HMI_VALUEi\":0,\"PI_VALUEf\":0.0,\"PI_VALUEb\":null,\"HMI_READi\":0},{\"INDEX\":46,\"TAG\":\"HMI_Future_25\",\"HMI_VALUEb\":true,\"HMI_VALUEi\":0,\"PI_VALUEf\":0.0,\"PI_VALUEb\":null,\"HMI_READi\":0},{\"INDEX\":47,\"TAG\":\"HMI_Future_26\",\"HMI_VALUEb\":true,\"HMI_VALUEi\":0,\"PI_VALUEf\":0.0,\"PI_VALUEb\":null,\"HMI_READi\":0},{\"INDEX\":48,\"TAG\":\"HMI_Future_27\",\"HMI_VALUEb\":true,\"HMI_VALUEi\":0,\"PI_VALUEf\":0.0,\"PI_VALUEb\":null,\"HMI_READi\":0},{\"INDEX\":49,\"TAG\":\"HMI_Future_28\",\"HMI_VALUEb\":true,\"HMI_VALUEi\":0,\"PI_VALUEf\":0.0,\"PI_VALUEb\":null,\"HMI_READi\":0},{\"INDEX\":50,\"TAG\":\"RR1ABspeed_HMI\",\"HMI_VALUEb\":null,\"HMI_VALUEi\":0,\"PI_VALUEf\":0.12,\"PI_VALUEb\":null,\"HMI_READi\":0},{\"INDEX\":51,\"TAG\":\"RR1CDspeed_HMI\",\"HMI_VALUEb\":null,\"HMI_VALUEi\":0,\"PI_VALUEf\":0.12,\"PI_VALUEb\":null,\"HMI_READi\":0},{\"INDEX\":52,\"TAG\":\"RR2ABspeed_HMI\",\"HMI_VALUEb\":null,\"HMI_VALUEi\":0,\"PI_VALUEf\":0.12,\"PI_VALUEb\":null,\"HMI_READi\":0},{\"INDEX\":53,\"TAG\":\"Switch1Main_HMIb\",\"HMI_VALUEb\":null,\"HMI_VALUEi\":0,\"PI_VALUEf\":0.12,\"PI_VALUEb\":false,\"HMI_READi\":0},{\"INDEX\":54,\"TAG\":\"open\",\"HMI_VALUEb\":null,\"HMI_VALUEi\":0,\"PI_VALUEf\":0.12,\"PI_VALUEb\":false,\"HMI_READi\":0},{\"INDEX\":55,\"TAG\":\"Switch2RR3Main_HMIb\",\"HMI_VALUEb\":null,\"HMI_VALUEi\":0,\"PI_VALUEf\":0.12,\"PI_VALUEb\":false,\"HMI_READi\":0},{\"INDEX\":56,\"TAG\":\"open\",\"HMI_VALUEb\":null,\"HMI_VALUEi\":0,\"PI_VALUEf\":0.12,\"PI_VALUEb\":false,\"HMI_READi\":0},{\"INDEX\":57,\"TAG\":\"Switch3RR4Main_HMIb\",\"HMI_VALUEb\":null,\"HMI_VALUEi\":null,\"PI_VALUEf\":0.12,\"PI_VALUEb\":true,\"HMI_READi\":0},{\"INDEX\":58,\"TAG\":\"open\",\"HMI_VALUEb\":null,\"HMI_VALUEi\":0,\"PI_VALUEf\":0.12,\"PI_VALUEb\":false,\"HMI_READi\":0},{\"INDEX\":59,\"TAG\":\"Switch4RR3Main_HMIb\",\"HMI_VALUEb\":null,\"HMI_VALUEi\":0,\"PI_VALUEf\":0.12,\"PI_VALUEb\":false,\"HMI_READi\":0},{\"INDEX\":60,\"TAG\":\"open\",\"HMI_VALUEb\":null,\"HMI_VALUEi\":0,\"PI_VALUEf\":0.12,\"PI_VALUEb\":false,\"HMI_READi\":0},{\"INDEX\":61,\"TAG\":\"Switch5Main_HMIb\",\"HMI_VALUEb\":null,\"HMI_VALUEi\":0,\"PI_VALUEf\":0.12,\"PI_VALUEb\":false,\"HMI_READi\":0},{\"INDEX\":62,\"TAG\":\"open\",\"HMI_VALUEb\":null,\"HMI_VALUEi\":0,\"PI_VALUEf\":0.12,\"PI_VALUEb\":true,\"HMI_READi\":0},{\"INDEX\":63,\"TAG\":\"Switch6Main_HMIb\",\"HMI_VALUEb\":null,\"HMI_VALUEi\":0,\"PI_VALUEf\":0.12,\"PI_VALUEb\":false,\"HMI_READi\":0},{\"INDEX\":64,\"TAG\":\"RR2orRR3Pwr_HMIb\",\"HMI_VALUEb\":null,\"HMI_VALUEi\":0,\"PI_VALUEf\":0.12,\"PI_VALUEb\":false,\"HMI_READi\":0},{\"INDEX\":65,\"TAG\":\"TramStn1_HMIb\",\"HMI_VALUEb\":null,\"HMI_VALUEi\":0,\"PI_VALUEf\":0.12,\"PI_VALUEb\":false,\"HMI_READi\":0},{\"INDEX\":66,\"TAG\":\"TramStn2_HMIb\",\"HMI_VALUEb\":null,\"HMI_VALUEi\":0,\"PI_VALUEf\":0.12,\"PI_VALUEb\":false,\"HMI_READi\":0},{\"INDEX\":67,\"TAG\":\"TramStn3_HMIb\",\"HMI_VALUEb\":null,\"HMI_VALUEi\":0,\"PI_VALUEf\":0.12,\"PI_VALUEb\":false,\"HMI_READi\":0},{\"INDEX\":68,\"TAG\":\"TramStn4_HMIb\",\"HMI_VALUEb\":null,\"HMI_VALUEi\":0,\"PI_VALUEf\":0.12,\"PI_VALUEb\":true,\"HMI_READi\":0},{\"INDEX\":69,\"TAG\":\"TramStn5_HMIb\",\"HMI_VALUEb\":null,\"HMI_VALUEi\":0,\"PI_VALUEf\":0.12,\"PI_VALUEb\":false,\"HMI_READi\":0},{\"INDEX\":70,\"TAG\":\"TramStn6_HMIb\",\"HMI_VALUEb\":null,\"HMI_VALUEi\":0,\"PI_VALUEf\":0.12,\"PI_VALUEb\":false,\"HMI_READi\":0},{\"INDEX\":71,\"TAG\":\"PI_Future_1\",\"HMI_VALUEb\":null,\"HMI_VALUEi\":0,\"PI_VALUEf\":0.12,\"PI_VALUEb\":false,\"HMI_READi\":0},{\"INDEX\":72,\"TAG\":\"PI_Future_2\",\"HMI_VALUEb\":null,\"HMI_VALUEi\":0,\"PI_VALUEf\":0.12,\"PI_VALUEb\":false,\"HMI_READi\":0},{\"INDEX\":73,\"TAG\":\"PI_Future_3\",\"HMI_VALUEb\":null,\"HMI_VALUEi\":0,\"PI_VALUEf\":0.12,\"PI_VALUEb\":false,\"HMI_READi\":0},{\"INDEX\":74,\"TAG\":\"PI_Future_4\",\"HMI_VALUEb\":null,\"HMI_VALUEi\":0,\"PI_VALUEf\":0.12,\"PI_VALUEb\":false,\"HMI_READi\":0},{\"INDEX\":75,\"TAG\":\"PI_Future_5\",\"HMI_VALUEb\":null,\"HMI_VALUEi\":0,\"PI_VALUEf\":0.12,\"PI_VALUEb\":false,\"HMI_READi\":0},{\"INDEX\":76,\"TAG\":\"PI_Future_6\",\"HMI_VALUEb\":null,\"HMI_VALUEi\":0,\"PI_VALUEf\":0.12,\"PI_VALUEb\":false,\"HMI_READi\":0},{\"INDEX\":77,\"TAG\":\"PI_Future_6\",\"HMI_VALUEb\":null,\"HMI_VALUEi\":0,\"PI_VALUEf\":0.12,\"PI_VALUEb\":false,\"HMI_READi\":0},{\"INDEX\":78,\"TAG\":\"PI_Future_8\",\"HMI_VALUEb\":null,\"HMI_VALUEi\":0,\"PI_VALUEf\":0.12,\"PI_VALUEb\":false,\"HMI_READi\":0},{\"INDEX\":79,\"TAG\":\"PI_Future_9\",\"HMI_VALUEb\":null,\"HMI_VALUEi\":0,\"PI_VALUEf\":0.12,\"PI_VALUEb\":false,\"HMI_READi\":0},{\"INDEX\":80,\"TAG\":\"PI_Future_10\",\"HMI_VALUEb\":null,\"HMI_VALUEi\":0,\"PI_VALUEf\":0.12,\"PI_VALUEb\":false,\"HMI_READi\":0}]\"\n";
    private JSONOperatorServiceStub jsonOperatorServiceStub;

    @BeforeEach
    void setUp() {
        HMIJSONDAOStub hmiJsonDaoStub = new HMIJSONDAOStub(new HashMap<>());
        jsonOperatorServiceStub = new JSONOperatorServiceStub(hmiJsonDaoStub);
    }

    @Test
    void testReadHmiDataMapFromFile() throws IOException {
        Map<String, HmiData> hmiDataMap = jsonOperatorServiceStub.readHmiDataMapFromFile(FILE_PATH);

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

    @Test
    void testProcessData() throws IOException {
        Map<String, HmiData> hmiDataMap = jsonOperatorServiceStub.readHmiDataMapFromFile(FILE_PATH);
        HmiData data1 = hmiDataMap.get("1");
        HmiData data14 = hmiDataMap.get("14");
        hmiDataMap.forEach((key, value) -> System.out.println(value));

        assertEquals("HMI_RHT", data1.getTag());
        assertEquals("HMI_Switch4RR3b", data14.getTag());
    }

    @Test
    void testUpdateValue() throws IOException {
        Map<String, HmiData> hmiDataMap = jsonOperatorServiceStub.readHmiDataMapFromFile(FILE_PATH);
        HmiData data1 = hmiDataMap.get("1");

        jsonOperatorServiceStub.updateValue(data1, "HMI_VALUEi", 33);

        assertEquals(33, data1.getHmiValuei());
        assertEquals(1, data1.getHmiReadi());
    }

    @Test
    void testUpdateFile() throws IOException {
        Map<String, HmiData> hmiDataMap = jsonOperatorServiceStub.readHmiDataMapFromFile(FILE_PATH);
        HmiData data1 = hmiDataMap.get("1");

        jsonOperatorServiceStub.updateValue(data1, "HMI_VALUEi", 44);

        assertEquals(44, data1.getHmiValuei());
        assertEquals(1, data1.getHmiReadi());

        jsonOperatorServiceStub.writeMapToFile(hmiDataMap, TEST_FILE_PATH_CHANGE);

        Map<String, HmiData> newDataMap = jsonOperatorServiceStub.readHmiDataMapFromFile(TEST_FILE_PATH_CHANGE);
        HmiData dataNew1 = newDataMap.get("1");

        assertEquals(44, dataNew1.getHmiValuei());
    }

    @Test
    void testCompareAndSetHMI_READi() throws IOException {
        Map<String, HmiData> hmiDataMap = jsonOperatorServiceStub.readHmiDataMapFromFile(FILE_PATH);
        Map<String, HmiData> workMap = jsonOperatorServiceStub.readHmiDataMapFromFile(FILE_PATH);

        hmiDataMap.get("1").setHmiReadi(1);

        jsonOperatorServiceStub.compareAndSetHMI_READi(hmiDataMap, workMap);

        assertEquals(0, hmiDataMap.get("1").getHmiReadi());
    }

    @Test
    void serverTestStringToJSONObject() throws IOException {
        assertNotNull(jsonOperatorServiceStub.writeStringToMap(TEST_SERVER_STRING_FULL));
        System.out.println(jsonOperatorServiceStub.writeStringToMap(TEST_SERVER_STRING_FULL));
    }

    @Test
    void testUpdateValueHMI_READi() throws IOException {
        Map<String, HmiData> hmiDataMap = jsonOperatorServiceStub.readHmiDataMapFromFile(FILE_PATH);
        HmiData data1 = hmiDataMap.get("1");

        jsonOperatorServiceStub.updateValue(data1, "HMI_VALUEi", 33);

        assertEquals(33, data1.getHmiValuei());
        assertEquals(1, data1.getHmiReadi());
    }

    @Test
    void testUpdateMap() throws IOException {
        Map<String, HmiData> hmiDataMap = jsonOperatorServiceStub.readHmiDataMapFromFile(FILE_PATH);
        HmiData data1 = hmiDataMap.get("1");

        jsonOperatorServiceStub.updateValue(data1, "HMI_VALUEi", 44);

        assertEquals(44, data1.getHmiValuei());
        assertEquals(1, data1.getHmiReadi());

        jsonOperatorServiceStub.writeMapToFile(hmiDataMap, TEST_FILE_PATH_CHANGE);

        Map<String, HmiData> newDataMap = jsonOperatorServiceStub.readHmiDataMapFromFile(TEST_FILE_PATH_CHANGE);
        HmiData dataNew1 = newDataMap.get("1");

        assertEquals(44, dataNew1.getHmiValuei());
    }

    @Test
    void checkTheSize() throws IOException {
        Map<String, HmiData> hmiDataMap = jsonOperatorServiceStub.readHmiDataMapFromFile(FILE_PATH);
        assertEquals(80, hmiDataMap.size());
    }
}