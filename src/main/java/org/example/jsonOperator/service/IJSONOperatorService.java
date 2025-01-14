package org.example.jsonOperator.service;

import org.example.jsonOperator.dto.HmiData;

import java.io.IOException;
import java.util.Map;

public interface IJSONOperatorService {
    Map<String, HmiData> readHmiDataMapFromFile(String filePath) throws IOException;
    void updateValue(HmiData data, String variableName, Object newValue);
    void compareAndSetHMI_READi(Map<String, HmiData> hmiDataMap, Map<String, HmiData> workMap);
    Map<String, HmiData> writeStringToMap(String jsonString) throws IOException;
    void writeMapToFile(Map<String, ?> map, String filePath) throws IOException;
    String writeMapToString(Map<String, HmiData> map) throws IOException;
    void printMap(Map<String, HmiData> map);
}