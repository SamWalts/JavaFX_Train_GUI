package org.viewModels;

import javafx.beans.property.SimpleStringProperty;
import javafx.beans.property.StringProperty;
import org.example.jsonOperator.dto.HmiData;
import org.services.DAOService;
import org.services.HMIChangeListener;
import org.services.HMIControllerInterface;

public class TitleViewModel implements HMIControllerInterface {
    private final StringProperty testLabelText = new SimpleStringProperty("Waiting for data...");

    public TitleViewModel() {
        DAOService daoService = DAOService.getInstance();
        new HMIChangeListener(daoService.getHmiJsonDao(), this);
    }

    @Override
    public void onMapUpdate(String key, Object oldValue, Object newValue) {
        if (newValue instanceof HmiData data && data.getTag() != null) {
            // Example: Update label when a specific tag changes
            if ("HMI_TramStopTime".equals(data.getTag())) {
                testLabelText.set("Tram stop time: " + data.getHmiValuei());
            }
        }
    }

    public StringProperty testLabelTextProperty() {
        return testLabelText;
    }
}