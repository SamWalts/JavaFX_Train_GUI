package org.viewModels;

import javafx.beans.property.*;
import org.example.jsonOperator.dto.HmiData;
import org.services.DAOService;
import org.services.HMIChangeListener;
import org.services.HMIControllerInterface;
import org.services.UIStateService;

import java.util.Map;
import java.util.Optional;
import java.util.Set;
import java.util.concurrent.ConcurrentHashMap;

public class TrainViewModel implements HMIControllerInterface {

    private final BooleanProperty dieselMode = new SimpleBooleanProperty(true);
    private final BooleanProperty hornVisible = new SimpleBooleanProperty();
    private final BooleanProperty whistleVisible = new SimpleBooleanProperty();
    private final BooleanProperty bellVisible = new SimpleBooleanProperty();

    private final StringProperty rr1abSpeed = new SimpleStringProperty("0.0");
    private final StringProperty rr1cdSpeed = new SimpleStringProperty("0.0");
    private final StringProperty rr2abSpeed = new SimpleStringProperty("0.0");

    private final Map<String, BooleanProperty> switchStates = new ConcurrentHashMap<>();
    private final DAOService daoService;

    public TrainViewModel() {
        this.daoService = DAOService.getInstance();
        new HMIChangeListener(daoService.getHmiJsonDao(), this);

        initializeSwitchStates();

        // Bind sound control visibility to the diesel/steam mode
        hornVisible.bind(dieselMode);
        whistleVisible.bind(dieselMode.not());
        bellVisible.bind(dieselMode.not());

        System.out.println("TrainViewModel initialized.");
    }

    private void initializeSwitchStates() {
        // Tags must match the "TAG" in your JSON for the switches
        switchStates.put("HMI_Switch1ABb", new SimpleBooleanProperty(false));
        switchStates.put("HMI_Switch2RR3b", new SimpleBooleanProperty(false));
        switchStates.put("HMI_Switch3RR4b", new SimpleBooleanProperty(false));
        switchStates.put("HMI_Switch4RR3b", new SimpleBooleanProperty(false));
        switchStates.put("HMI_Switch5ABb", new SimpleBooleanProperty(false));
        switchStates.put("HMI_Switch6ABb", new SimpleBooleanProperty(false));
    }

    @Override
    public void onMapUpdate(String key, Object oldValue, Object newValue) {
        if (!(newValue instanceof HmiData)) return;
        HmiData data = (HmiData) newValue;

        // Acknowledge pending keys if server cleared HMI_READi
        UIStateService.getInstance().checkAck(key, data);

        String tag = data.getTag();
        if (tag == null) return;

        // Update switch state from incoming data (PI_VALUEb)
        if (switchStates.containsKey(tag) && data.getPiValueb() != null) {
            switchStates.get(tag).set(data.getPiValueb());
        }

        // Update other properties based on incoming data
        switch (tag) {
            case "HMI_RRDieselSteamb" -> {
                if (data.getHmiValueb() != null) dieselMode.set(data.getHmiValueb());
            }
            case "RR1ABspeed_HMI" -> {
                if (data.getPiValuef() != null) rr1abSpeed.set(String.format("%.2f", data.getPiValuef()));
            }
            case "RR1CDspeed_HMI" -> {
                if (data.getPiValuef() != null) rr1cdSpeed.set(String.format("%.2f", data.getPiValuef()));
            }
            case "RR2ABspeed_HMI" -> {
                if (data.getPiValuef() != null) rr2abSpeed.set(String.format("%.2f", data.getPiValuef()));
            }
        }
    }

    /**
     * Finds an HmiData object by its tag.
     */
    private Optional<HmiData> findDataByTag(String tag) {
        return daoService.getHmiDataMap().values().stream()
                .filter(d -> tag.equals(d.getTag()))
                .findFirst();
    }

    /**
     * Action to toggle a switch state. This updates HMI_VALUEb and signals a change.
     * The backend is expected to reflect this change in PI_VALUEb.
     */
    public void toggleSwitch(String tag) {
        findDataByTag(tag).ifPresent(data -> {
            boolean currentState = data.getHmiValueb() != null && data.getHmiValueb();
            UIStateService.getInstance().markPending(Set.of(String.valueOf(data.getIndex())));
            data.setHmiValueb(!currentState);
            data.setHmiReadi(2);
            // Putting the data back triggers the listener and notifies the backend
            daoService.getHmiDataMap().put(String.valueOf(data.getIndex()), data);
        });
    }

    /**
     * Generic action for simple boolean toggles like Horn, Bell, Whistle.
     */
    public void toggleHmiAction(String tag) {
        findDataByTag(tag).ifPresent(data -> {
            boolean currentState = data.getHmiValueb() != null && data.getHmiValueb();
            UIStateService.getInstance().markPending(Set.of(String.valueOf(data.getIndex())));
            data.setHmiValueb(!currentState);
            data.setHmiReadi(2);
            daoService.getHmiDataMap().put(String.valueOf(data.getIndex()), data);
        });
    }

    // Property Getters
    public BooleanProperty getSwitchStateProperty(String tag) { return switchStates.get(tag); }
    public BooleanProperty hornVisibleProperty() { return hornVisible; }
    public BooleanProperty whistleVisibleProperty() { return whistleVisible; }
    public BooleanProperty bellVisibleProperty() { return bellVisible; }
    public StringProperty rr1abSpeedProperty() { return rr1abSpeed; }
    public StringProperty rr1cdSpeedProperty() { return rr1cdSpeed; }
    public StringProperty rr2abSpeedProperty() { return rr2abSpeed; }
}