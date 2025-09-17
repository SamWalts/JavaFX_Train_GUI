package org.viewModels;

import javafx.application.Platform;
import javafx.beans.property.*;
import javafx.collections.FXCollections;
import javafx.collections.ObservableList;
import org.example.jsonOperator.dto.HmiData;
import org.services.DAOService;
import org.services.HMIChangeListener;

import java.util.HashMap;
import java.util.Map;

public class TitleViewModel extends AbstractHmiViewModel {
    // List of per-index view models
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

    @Override
    protected void applyData(HmiData data, String key) {
        HmiDataViewModel viewModel = dataViewModels.get(key);
        if (viewModel != null) {
            viewModel.updateFromData(data);
        } else {
            // Add new entry if it passes the base filters (already ensured) and not present
            HmiDataViewModel newViewModel = new HmiDataViewModel(data, key);
            dataViewModels.put(key, newViewModel);
            hmiDataList.add(newViewModel);
        }
    }

    public ObservableList<HmiDataViewModel> getHmiDataList() { return hmiDataList; }

    // Expose inherited json string property for binding
    public StringProperty jsonStringProperty() { return super.jsonStringProperty(); }

    // Inner class for individual HMI data binding to help test the list of all data
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

        public StringProperty tagProperty() { return tag; }
        public IntegerProperty hmiValueiProperty() { return hmiValuei; }
        public BooleanProperty hmiValuebProperty() { return hmiValueb; }
        public FloatProperty piValuefProperty() { return piValuef; }
        public BooleanProperty piValuebProperty() { return piValueb; }
        public IntegerProperty hmiReadiProperty() { return hmiReadi; }
        public String getKey() { return key; }
    }
}