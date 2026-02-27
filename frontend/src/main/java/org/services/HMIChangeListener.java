package org.services;

import javafx.application.Platform;
import org.example.jsonOperator.dao.HMIJSONDAOSingleton;

import org.example.jsonOperator.dao.ListenerConcurrentMap;
import org.example.jsonOperator.dto.HmiData;

public class HMIChangeListener {
    private final HMIJSONDAOSingleton hmiJsonDao;
    private final HMIControllerInterface controller;
    private ListenerConcurrentMap.Listener<String, HmiData> listener;

    public HMIChangeListener(HMIJSONDAOSingleton hmiJsonDao, HMIControllerInterface controller) {
        this.hmiJsonDao = hmiJsonDao;
        this.controller = controller;
        setupListener();

        // Immediately process all existing entries to populate the UI with initial state.
        hmiJsonDao.fetchAll().forEach((key, value) -> {
            Platform.runLater(() -> controller.onMapUpdate(key, null, value));
        });
    }

    private void setupListener() {
        System.out.println("Setting up listener...");
        try {
            listener = new ListenerConcurrentMap.Listener<String, HmiData>() {
                @Override
                public void onPut(String key, HmiData value) {
                    System.out.println("Listener onPut called: key=" + key);
                    Platform.runLater(() -> controller.onMapUpdate(key, null, value));
                }

                @Override
                public void onRemove(String key, HmiData value) {
                    System.out.println("Listener onRemove called: key=" + key);
                    Platform.runLater(() -> controller.onMapUpdate(key, value, null));
                }
            };
            hmiJsonDao.fetchAll().addListener(listener);
            System.out.println("Listener setup complete");
        } catch (Exception e) {
            System.err.println("Failed to set up listener: " + e.getMessage());
        }
    }

    /**
     * Removes the listener from the map.
     * Call this when the associated controller/screen is being disposed.
     */
    public void cleanup() {
        if (listener != null && hmiJsonDao != null) {
            System.out.println("Removing HMI change listener...");
            hmiJsonDao.fetchAll().removeListener(listener);
            listener = null;
            System.out.println("HMI change listener removed");
        }
    }

    /**
     * Returns true if this listener is still active.
     */
    public boolean isActive() {
        return listener != null;
    }
}