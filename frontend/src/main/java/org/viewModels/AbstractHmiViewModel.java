package org.viewModels;

import javafx.application.Platform;
import javafx.beans.property.SimpleStringProperty;
import javafx.beans.property.StringProperty;
import org.example.jsonOperator.dto.HmiData;
import org.services.HMIControllerInterface;
import org.services.UIStateService;

/**
 * Abstract base class that centralizes common HMI map update handling.
 * Responsibilities:
 *  - Filtering incoming map updates (null tag, "open", "Future").
 *  - Acknowledging pending UI actions via UIStateService.
 *  - Building a human-readable JSON-like string of the latest update.
 *  - Ensuring all UI-related work executes on the JavaFX Application Thread.
 *  - Delegating concrete property/list updates to {@link #applyData(HmiData, String)}.
 */
public abstract class AbstractHmiViewModel implements HMIControllerInterface {

    private final StringProperty jsonStringProperty = new SimpleStringProperty("No updates yet");

    /**
     * Final implementation of onMapUpdate to guarantee consistent behavior across subclasses.
     */
    @Override
    public final void onMapUpdate(String key, Object oldValue, Object newValue) {
        if (!(newValue instanceof HmiData)) return;
        HmiData data = (HmiData) newValue;
        String tag = data.getTag();
        if (tag == null) return;
        if (tag.contains("open") || tag.contains("Future")) return; // filter out unwanted entries

        // Acknowledge pending change if server cleared/updated state
        UIStateService.getInstance().checkAck(key, data);

        // Ensure UI thread for downstream updates
        Platform.runLater(() -> {
            jsonStringProperty.set(buildJsonString(data));
            applyData(data, key);
        });
    }

    /**
     * Subclasses implement their specific property/list update logic here.
     * This method is always invoked on the JavaFX Application Thread.
     *
     * @param data latest HmiData for the given key
     * @param key  the map key (string version of index)
     */
    protected abstract void applyData(HmiData data, String key);

    /**
     * Helper to construct a readable JSON-like representation for binding/diagnostics.
     */
    protected String buildJsonString(HmiData data) {
        StringBuilder jsonBuilder = new StringBuilder();
        jsonBuilder.append("Latest Update:\n{");
        jsonBuilder.append("\n  \"INDEX\": ").append(data.getIndex());
        jsonBuilder.append(",\n  \"TAG\": \"").append(data.getTag() != null ? data.getTag() : "null").append("\"");
        jsonBuilder.append(",\n  \"HMI_VALUEi\": ").append(data.getHmiValuei());
        jsonBuilder.append(",\n  \"HMI_VALUEb\": ").append(data.getHmiValueb());
        jsonBuilder.append(",\n  \"PI_VALUEf\": ").append(data.getPiValuef());
        jsonBuilder.append(",\n  \"PI_VALUEb\": ").append(data.getPiValueb());
        jsonBuilder.append(",\n  \"HMI_READi\": ").append(data.getHmiReadi());
        jsonBuilder.append("\n}");
        return jsonBuilder.toString();
    }

    public StringProperty jsonStringProperty() { return jsonStringProperty; }
    public String getJsonString() { return jsonStringProperty.get(); }
}
