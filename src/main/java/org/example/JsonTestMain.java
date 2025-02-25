package org.example;

import org.example.jsonOperator.dao.HMIJSONDAOStub;
import org.example.jsonOperator.dao.IHMIJSONDAO;
import org.example.jsonOperator.service.IJSONOperatorService;
import org.example.jsonOperator.dto.HmiData;
import org.example.jsonOperator.service.JSONOperatorServiceStub;

import java.io.IOException;
import java.util.HashMap;
import java.util.Map;

public class JsonTestMain {

    private static final String FILE_PATH = "PiHmiDict.json";

    public static void main(String[] args) {
        try {
            IHMIJSONDAO<HmiData> hmiJsonDaoStub = new HMIJSONDAOStub(new HashMap<>());
            IJSONOperatorService jsonOperatorServiceStub = new JSONOperatorServiceStub(hmiJsonDaoStub);

            // Deserialize the JSON file into a map of HmiData objects
            Map<String, HmiData> hmiDataMap = jsonOperatorServiceStub.readHmiDataMapFromFile(FILE_PATH);

            // Create a work map to track original values for comparison
            Map<String, HmiData> workMap = new HashMap<>(hmiDataMap);

            jsonOperatorServiceStub.printMap(hmiDataMap);
            jsonOperatorServiceStub.writeMapToString(hmiDataMap);
            // Compare and set HMI_READi
            jsonOperatorServiceStub.compareAndSetHMI_READi(hmiDataMap, workMap);
        } catch (IOException e) {
            throw new RuntimeException(e);
        }



    }

    private static void processData(HmiData data) {
        System.out.println(data);
        String tagValue = data.getTag();
        System.out.println("Value of TAG is: " + tagValue);
    }

    private static void updateValue(HmiData data, String variableName, Object newValue) {
        if (variableName.equals("HMI_READi")) {
            data.setHmiReadi(2);
        }
        switch (variableName) {
            case "HMI_VALUEi":
                data.setHmiValuei((Integer) newValue);
                data.setHmiReadi(2);
                break;
            case "HMI_VALUEb":
                data.setHmiValueb((Boolean) newValue);
                data.setHmiReadi(2);
                break;
            case "PI_VALUEf":
                data.setPiValuef((Float) newValue);
                data.setHmiReadi(2);
                break;
            case "PI_VALUEb":
                data.setPiValueb((Boolean) newValue);
                data.setHmiReadi(2);
                break;
            default:
                throw new IllegalArgumentException("Unknown variable name: " + variableName);
        }
        System.out.println("Updated " + variableName + " to " + newValue);
    }
}