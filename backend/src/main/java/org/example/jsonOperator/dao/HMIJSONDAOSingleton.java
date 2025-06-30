package org.example.jsonOperator.dao;

import org.example.jsonOperator.dto.HmiData;
import com.fasterxml.jackson.databind.ObjectMapper;
import java.io.IOException;
import java.io.InputStream;
import java.util.Map;

public class HMIJSONDAOSingleton implements IHMIJSONDAO<HmiData> {
    // Singleton instance
    private static volatile HMIJSONDAOSingleton instance;

    // Shared data map between backend and frontend
    private ListenerConcurrentMap<String, HmiData> hmiDataMap;

    // Private constructor to prevent instantiation
    private HMIJSONDAOSingleton() {
        hmiDataMap = new ListenerConcurrentMap<>();
        loadInitialData();
    }

    // Thread-safe singleton access with double-checked locking
    public static HMIJSONDAOSingleton getInstance() {
        if (instance == null) {
            synchronized (HMIJSONDAOSingleton.class) {
                if (instance == null) {
                    instance = new HMIJSONDAOSingleton();
                }
            }
        }
        return instance;
    }

    // Load initial data from JSON file
    private void loadInitialData() {
        try {
            ObjectMapper mapper = new ObjectMapper();
            InputStream is = getClass().getClassLoader().getResourceAsStream("PiHmiDict.json");
            if (is != null) {
                Map<String, HmiData> initialData = mapper.readValue(is,
                        mapper.getTypeFactory().constructMapType(Map.class, String.class, HmiData.class));
                hmiDataMap.putAll(initialData);
            }
        } catch (IOException e) {
            e.printStackTrace();
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
    public ListenerConcurrentMap<String, HmiData> setAll(ListenerConcurrentMap<String, HmiData> newHmiDataMap) {
        this.hmiDataMap = newHmiDataMap;
        return this.hmiDataMap;
    }

    @Override
    public void setHmiDataMap(ListenerConcurrentMap<String, HmiData> hmiDataMap) {
        this.hmiDataMap = hmiDataMap;
    }

    // Additional utility methods for data manipulation
    public void updateHmiValue(String id, HmiData newData) {
        hmiDataMap.put(id, newData);
    }

    public boolean containsKey(String id) {
        return hmiDataMap.containsKey(id);
    }

    public int size() {
        return hmiDataMap.size();
    }
}