package org.example.jsonOperator.dao;

import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.example.jsonOperator.dto.HmiData;

import java.io.IOException;
import java.io.InputStream;
import java.util.Map;
import java.util.Objects;

public class HMIJSONDAOStub implements IHMIJSONDAO<HmiData> {

    private ListenerConcurrentMap<String, HmiData> hmiDataMap = new ListenerConcurrentMap<>();

    public HMIJSONDAOStub() {
        // Load initial data from JSON file
//        loadDataFromJSON();
    }


    private void loadDataFromJSON() {
        try (InputStream inputStream = getClass().getClassLoader().getResourceAsStream("PiHmiDict.json")) {
            if (inputStream == null) {
                throw new IOException("Cannot find PiHmiDict.json");
            }
            ObjectMapper objectMapper = new ObjectMapper();
            TypeReference<Map<String, HmiData>> typeRef = new TypeReference<>() {};
            Map<String, HmiData> initialData = objectMapper.readValue(inputStream, typeRef);
            hmiDataMap.putAll(initialData);
        } catch (IOException e) {
            e.printStackTrace();
            // Handle exception, maybe log it or throw a custom exception
        }
    }

    @Override
    public HmiData fetch(String id) {
        return hmiDataMap.get(id);
    }

    @Override
    public ListenerConcurrentMap<String, HmiData> fetchAll() {
        return hmiDataMap;
    }

    @Override
    public ListenerConcurrentMap<String, HmiData> setAll(ListenerConcurrentMap<String, HmiData> hmiDataMap) {
        this.hmiDataMap.clear();
        this.hmiDataMap.putAll(hmiDataMap);
        return this.hmiDataMap;
    }

    @Override
    public void setHmiDataMap(ListenerConcurrentMap<String, HmiData> hmiDataMap) {
        this.hmiDataMap = hmiDataMap;
    }

    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (o == null || getClass() != o.getClass()) return false;
        HMIJSONDAOStub that = (HMIJSONDAOStub) o;
        return Objects.equals(hmiDataMap, that.hmiDataMap);
    }

    @Override
    public int hashCode() {
        return Objects.hash(hmiDataMap);
    }
}