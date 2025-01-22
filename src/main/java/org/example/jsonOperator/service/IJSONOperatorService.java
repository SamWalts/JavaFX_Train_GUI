package org.example.jsonOperator.service;

import org.example.jsonOperator.dao.ListenerConcurrentMap;
import org.example.jsonOperator.dto.HmiData;

import java.io.IOException;
import java.util.Map;

public interface IJSONOperatorService {
    ListenerConcurrentMap<String, HmiData> readHmiDataMapFromFile(String filePath) throws IOException;
    void updateValue(HmiData data, String variableName, Object newValue);
    void compareAndSetHMI_READi(ListenerConcurrentMap<String, HmiData> hmiDataMap, ListenerConcurrentMap<String, HmiData> workMap);
    Map<String, HmiData> writeStringToMap(String jsonString) throws IOException;
    void writeMapToFile(ListenerConcurrentMap<String, ?> map, String filePath) throws IOException;
    String writeMapToString(ListenerConcurrentMap<String, HmiData> map) throws IOException;
    void printMap(ListenerConcurrentMap<String, HmiData> map);
}