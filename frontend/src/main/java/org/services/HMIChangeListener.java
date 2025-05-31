package org.services;

import javafx.application.Platform;
import org.example.jsonOperator.dao.HMIJSONDAOStub;
import org.example.jsonOperator.dao.ListenerConcurrentMap;
import org.example.jsonOperator.dto.HmiData;

public class HMIChangeListener {
    private final HMIJSONDAOStub hmiJsonDao;
    private final HMIControllerInterface controller;

    public HMIChangeListener(HMIJSONDAOStub hmiJsonDao, HMIControllerInterface controller) {
        this.hmiJsonDao = hmiJsonDao;
        this.controller = controller;
        setupListener();
    }

    private void setupListener() {
        System.out.println("Setting up listener...");
        try {
            hmiJsonDao.addListener(new ListenerConcurrentMap.Listener<String, HmiData>() {
                @Override
                public void onPut(String key, HmiData value) {
                    System.out.println("Listener onPut called: key=" + key + ", value=" + value);
                    Platform.runLater(() -> controller.onMapUpdate(key, null, value));
                }

                @Override
                public void onRemove(String key, HmiData value) {
                    System.out.println("Listener onRemove called: key=" + key + ", value=" + value);
                    Platform.runLater(() -> controller.onMapUpdate(key, value, null));
                }
            });
            System.out.println("Listener setup complete");
        } catch (Exception e) {
            System.err.println("Failed to set up listener: " + e.getMessage());
        }
    }
}