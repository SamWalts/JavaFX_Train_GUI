package org.services;

import org.example.jsonOperator.dao.HMIJSONDAOStub;
import org.example.jsonOperator.dao.ListenerConcurrentMap;
import org.example.jsonOperator.dto.HmiData;

/**
 * Singleton service that provides access to the shared DAO instance
 * across all controllers in the application.
 */
public class DAOService {
    private static DAOService instance;
    private final HMIJSONDAOStub hmiJsonDao;
    private final ListenerConcurrentMap<String, HmiData> hmiDataMap;

    private DAOService() {
        // Initialize the shared map and DAO
        this.hmiDataMap = new ListenerConcurrentMap<>();
        this.hmiJsonDao = new HMIJSONDAOStub(hmiDataMap);
    }

    public static synchronized DAOService getInstance() {
        if (instance == null) {
            instance = new DAOService();
        }
        return instance;
    }

    public HMIJSONDAOStub getHmiJsonDao() {
        return hmiJsonDao;
    }

    public ListenerConcurrentMap<String, HmiData> getHmiDataMap() {
        return hmiDataMap;
    }

    public void setHmiJsonDao(HMIJSONDAOStub populatedDao) {
    }
}