package org.example.jsonOperator.dao;

import org.example.jsonOperator.dto.HmiData;


import java.util.Map;

public class HMIJSONDAOStub implements IHMIJSONDAO<HmiData> {

    private ListenerConcurrentMap<String, HmiData> hmiDataMap;

    public HMIJSONDAOStub(ListenerConcurrentMap<String, HmiData> hmiDataMap) {
        this.hmiDataMap = hmiDataMap;
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
        this.hmiDataMap = hmiDataMap;
        return this.hmiDataMap;
    }

    @Override
    public void setHmiDataMap(ListenerConcurrentMap<String, HmiData> hmiDataMap) {
        this.hmiDataMap = hmiDataMap;
    }
}