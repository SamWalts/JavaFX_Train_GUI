package org.example.jsonOperator.dao;

import org.example.jsonOperator.dto.HmiData;

public interface IHMIJSONDAO<T>{

    HmiData fetch(String id);
    ListenerConcurrentMap<String, HmiData> fetchAll();
    ListenerConcurrentMap<String, HmiData> setAll(ListenerConcurrentMap<String, HmiData> hmiDataMap);
    void setHmiDataMap(ListenerConcurrentMap<String, HmiData> hmiDataMap);

}
