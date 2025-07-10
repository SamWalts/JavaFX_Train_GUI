package org.viewModels;

import javafx.application.Platform;
import javafx.beans.property.*;
import javafx.collections.FXCollections;
import javafx.collections.ObservableList;
import org.example.jsonOperator.dto.HmiData;
import org.services.DAOService;
import org.services.HMIChangeListener;
import org.services.HMIControllerInterface;

import java.util.HashMap;
import java.util.Map;

public class TitleViewModel implements HMIControllerInterface {
    private final StringProperty jsonStringProperty = new SimpleStringProperty("No updates yet");
    private final ObservableList<HmiDataViewModel> hmiDataList = FXCollections.observableArrayList();
    private final Map<String, HmiDataViewModel> dataViewModels = new HashMap<>();

    /**
     * Constructor for TitleViewModel.
     * Initializes the data view models and sets up the HMI change listener.
     */
    public TitleViewModel() {
        DAOService daoService = DAOService.getInstance();
        new HMIChangeListener(daoService.getHmiJsonDao(), this);
        initializeDataViewModels();
    }

    /**
     * Initializes the data view models from the DAOService.
     * This method is called on the JavaFX Application Thread to ensure UI updates are safe.
     */
    private void initializeDataViewModels() {
        Platform.runLater(() -> {
            for (int i = 1; i <= 80; i++) {
                HmiData data = DAOService.getInstance().getHmiDataMap().get(String.valueOf(i));
                if (data != null && data.getTag() != null && !data.getTag().contains("open") && !data.getTag().contains("Future")) {
                    HmiDataViewModel viewModel = new HmiDataViewModel(data, String.valueOf(i));
                    dataViewModels.put(String.valueOf(i), viewModel);
                    hmiDataList.add(viewModel);
                }
            }
        });
    }

    /**
     * This method is called when there is an update in the HMI data.
     * It updates the JSON string and the corresponding view model.
     *
     * @param key      The key of the updated data.
     * @param oldValue The old value (not used here).
     * @param newValue The new value of type HmiData.
     */
    @Override
    public void onMapUpdate(String key, Object oldValue, Object newValue) {
        System.out.println("TitleViewModel.onMapUpdate called - key: " + key + ", newValue: " + newValue);

        if (newValue instanceof HmiData data && data.getTag() != null && !data.getTag().contains("open") && !data.getTag().contains("Future")) {
            Platform.runLater(() -> {
                updateJsonString(data);

                // Update the specific data view model
                HmiDataViewModel viewModel = dataViewModels.get(key);
                if (viewModel != null) {
                    System.out.println("Updating ViewModel for key: " + key + " with data: " + data.getTag());
                    viewModel.updateFromData(data);
                } else {
                    System.out.println("No ViewModel found for key: " + key);
                    // Create new view model for new data
                    if (!data.getTag().contains("open")) {
                        HmiDataViewModel newViewModel = new HmiDataViewModel(data, key);
                        dataViewModels.put(key, newViewModel);
                        hmiDataList.add(newViewModel);
                    }
                }
            });
        }
    }

    private void updateJsonString(HmiData data) {
        StringBuilder jsonBuilder = new StringBuilder();
        jsonBuilder.append("Latest Update:\n{\n");
        jsonBuilder.append("  \"INDEX\": ").append(data.getIndex()).append(",\n");
        jsonBuilder.append("  \"TAG\": \"").append(data.getTag() != null ? data.getTag() : "null").append("\",\n");
        jsonBuilder.append("  \"HMI_VALUEi\": ").append(data.getHmiValuei()).append(",\n");
        jsonBuilder.append("  \"HMI_VALUEb\": ").append(data.getHmiValueb()).append(",\n");
        jsonBuilder.append("  \"PI_VALUEf\": ").append(data.getPiValuef()).append(",\n");
        jsonBuilder.append("  \"PI_VALUEb\": ").append(data.getPiValueb()).append(",\n");
        jsonBuilder.append("  \"HMI_READi\": ").append(data.getHmiReadi()).append("\n");
        jsonBuilder.append("}");
        jsonStringProperty.set(jsonBuilder.toString());
    }

    public StringProperty jsonStringProperty() {
        return jsonStringProperty;
    }

    public ObservableList<HmiDataViewModel> getHmiDataList() {
        return hmiDataList;
    }

    // Inner class for individual HMI data binding
    public static class HmiDataViewModel {
        private final StringProperty tag = new SimpleStringProperty();
        private final IntegerProperty hmiValuei = new SimpleIntegerProperty();
        private final BooleanProperty hmiValueb = new SimpleBooleanProperty();
        private final FloatProperty piValuef = new SimpleFloatProperty();
        private final BooleanProperty piValueb = new SimpleBooleanProperty();
        private final IntegerProperty hmiReadi = new SimpleIntegerProperty();
        private final String key;

        public HmiDataViewModel(HmiData data, String key) {
            this.key = key;
            updateFromData(data);
        }

        public void updateFromData(HmiData data) {
            tag.set(data.getTag());
            hmiValuei.set(data.getHmiValuei() != null ? data.getHmiValuei() : 0);
            hmiValueb.set(data.getHmiValueb() != null ? data.getHmiValueb() : false);
            piValuef.set(data.getPiValuef() != null ? data.getPiValuef() : 0.0f);
            piValueb.set(data.getPiValueb() != null ? data.getPiValueb() : false);
            hmiReadi.set(data.getHmiReadi() != null ? data.getHmiReadi() : 0);
        }

        // Getters for properties
        public StringProperty tagProperty() { return tag; }
        public IntegerProperty hmiValueiProperty() { return hmiValuei; }
        public BooleanProperty hmiValuebProperty() { return hmiValueb; }
        public FloatProperty piValuefProperty() { return piValuef; }
        public BooleanProperty piValuebProperty() { return piValueb; }
        public IntegerProperty hmiReadiProperty() { return hmiReadi; }
        public String getKey() { return key; }
    }
}