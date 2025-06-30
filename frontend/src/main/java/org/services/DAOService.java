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
        this.hmiJsonDao = new HMIJSONDAOStub();
    }

    /**
     * Returns the singleton instance of DAOService.
     * This method ensures that only one instance exists throughout the application.
     *
     * @return The singleton instance of DAOService.
     */
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

    /**
     * Sets the HMI JSON DAO with a populated instance.
     * This method is typically called at application startup to load initial data.
     *
     * @param populatedDao The populated HMI JSON DAO instance.
     */
    public void setHmiJsonDao(HMIJSONDAOStub populatedDao) {
        if (populatedDao != null && populatedDao.fetchAll() != null) {
            // Clear existing data and copy all data from the populated DAO.
            // This ensures the singleton service holds the data loaded at startup.
            this.hmiDataMap.clear();
            this.hmiDataMap.putAll(populatedDao.fetchAll());
        }
    }
}