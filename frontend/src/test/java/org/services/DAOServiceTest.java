package org.services;

import org.example.jsonOperator.dao.HMIJSONDAOStub;
import org.example.jsonOperator.dao.ListenerConcurrentMap;
import org.example.jsonOperator.dto.HmiData;
import org.junit.jupiter.api.Test;
import org.services.DAOService;

import static org.junit.jupiter.api.Assertions.*;

class DAOServiceTest {

    @Test
    void testSingletonInstance() {
        // Get two instances of DAOService
        DAOService instance1 = DAOService.getInstance();
        DAOService instance2 = DAOService.getInstance();

        // Verify they are the same instance
        assertSame(instance1, instance2, "DAOService should be a singleton");
    }

    @Test
    void testHmiJsonDaoInitialization() {
        // Get the DAOService instance
        DAOService daoService = DAOService.getInstance();

        // Verify the HMIJSONDAOStub is not null
        HMIJSONDAOStub dao = daoService.getHmiJsonDao();
        assertNotNull(dao, "HMIJSONDAOStub should be initialized");
    }

    @Test
    void testHmiDataMapInitialization() {
        // Get the DAOService instance
        DAOService daoService = DAOService.getInstance();

        // Verify the ListenerConcurrentMap is not null
        ListenerConcurrentMap<String, HmiData> map = daoService.getHmiDataMap();
        assertNotNull(map, "ListenerConcurrentMap should be initialized");
    }

    @Test
    void testSharedDataConsistency() {
        // Get the DAOService instance
        DAOService daoService = DAOService.getInstance();

        // Add a value to the map
        ListenerConcurrentMap<String, HmiData> map = daoService.getHmiDataMap();
        HmiData data = new HmiData();
        map.put("testKey", data);

        // Verify the value is accessible from the same map instance
        assertEquals(data, map.get("testKey"), "Data should be consistent across shared map");
    }

    //TODO: Add more tests for specific functionalities of the DAOService and HMIJSONDAOStub
}