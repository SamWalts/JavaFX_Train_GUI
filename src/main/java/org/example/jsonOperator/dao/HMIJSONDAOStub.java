package org.example.jsonOperator.dao;

import org.example.jsonOperator.dto.HmiData;

import java.util.Map;

public class HMIJSONDAOStub implements IHMIJSONDAO<HmiData> {

    private Map<String, HmiData> hmiDataMap;

    public HMIJSONDAOStub(Map<String, HmiData> hmiDataMap) {
        this.hmiDataMap = hmiDataMap;
    }

    @Override
    public HmiData fetch(String id) {
        return hmiDataMap.get(id);
    }

    @Override
    public Map<String, HmiData> fetchAll() {
        return hmiDataMap;
    }

    @Override
    public Map<String, HmiData> setAll(Map<String, HmiData> hmiDataMap) {
        return Map.of();
    }

    @Override
    public void setHmiDataMap(Map<String, HmiData> hmiDataMap) {
        this.hmiDataMap = hmiDataMap;
    }
}