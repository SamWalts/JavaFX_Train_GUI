package org.example.jsonOperator.dao;

import org.example.jsonOperator.dto.HmiData;

import java.util.Map;

public interface IHMIJSONDAO<T>{

    HmiData fetch(String id);
    Map<String, HmiData> fetchAll();
    Map<String, HmiData> setAll(Map<String, HmiData> hmiDataMap);
    void setHmiDataMap(Map<String, HmiData> hmiDataMap);

}
