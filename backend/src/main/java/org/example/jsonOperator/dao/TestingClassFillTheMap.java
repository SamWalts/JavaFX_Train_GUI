package org.example.jsonOperator.dao;

import org.example.jsonOperator.dto.HmiData;
import org.example.jsonOperator.service.JSONOperatorServiceStub;

import java.io.IOException;

public class TestingClassFillTheMap {

    HMIJSONDAOStub hmijsondaoStub = new HMIJSONDAOStub(new ListenerConcurrentMap<>());

    public static boolean loadDataFromJsonFile(HMIJSONDAOStub hmijsondaoStub) throws IOException {
        try {
            JSONOperatorServiceStub jsonOperatorServiceStub = new JSONOperatorServiceStub();
            String filePath = "PiHmiDict.json";
            ListenerConcurrentMap<String, HmiData> hmiDataMap = jsonOperatorServiceStub.readHmiDataMapFromFile(filePath);
            if (hmiDataMap == null) {
                System.err.println("Failed to load data from JSON file.");
                return false;
            } else {
                hmijsondaoStub.setHmiDataMap(hmiDataMap);
                System.out.println("Data loaded successfully from JSON file.");
                System.out.println("Map contains " + hmiDataMap.size() + " entries.");
                return true;
            }
        } catch (Exception e) {
            System.err.println("Error loading data from JSON file: " + e.getMessage());
            return false;
        }
    }

    /**
     * No-argument method for frontend to call that creates and populates a new DAO instance
     * @return true if successful, false otherwise
     */
    public static HMIJSONDAOStub populateNewDao() {
        HMIJSONDAOStub stub = new HMIJSONDAOStub(new ListenerConcurrentMap<>());
        try {
            boolean success = loadDataFromJsonFile(stub);
            if (success) {
                System.out.println("Successfully populated new DAO with JSON data");
                return stub;
            } else {
                System.err.println("Failed to populate DAO");
                return null;
            }
        } catch (Exception e) {
            System.err.println("Error populating DAO: " + e.getMessage());
            e.printStackTrace();
            return null;
        }
    }

    public static void main(String[] args) {
        populateNewDao();
    }
}
