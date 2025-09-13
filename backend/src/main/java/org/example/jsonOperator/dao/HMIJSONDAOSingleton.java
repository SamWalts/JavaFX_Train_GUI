package org.example.jsonOperator.dao;

import com.fasterxml.jackson.core.type.TypeReference;
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
    }

    // Thread-safe singleton access with double-checked locking
    public static HMIJSONDAOSingleton getInstance() {
        if (instance == null) {
            synchronized (HMIJSONDAOSingleton.class) {
                if (instance == null) {
                    instance = new HMIJSONDAOSingleton();
                    System.out.println("This is the HMIJSONDAOSingleton instance PID" + System.identityHashCode(instance));
                }
            }
        }
        System.out.println("This is the HMIJSONDAOSingleton instance PID" + System.identityHashCode(instance));
        return instance;
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
        // Modifies the content of the existing map object.
        this.hmiDataMap.clear();
        this.hmiDataMap.putAll(hmiDataMap);
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