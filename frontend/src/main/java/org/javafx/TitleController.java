package org.javafx;

import java.io.IOException;
import javafx.fxml.FXML;
import org.example.jsonOperator.dto.HmiData;
import org.services.HMIControllerInterface;
import javafx.scene.control.Label;


public class TitleController implements HMIControllerInterface {

    // This is the label we will test to hook up to the listener
    @FXML
    private Label testLabel;


    @Override
    public void onMapUpdate(String key, Object oldValue, Object newValue) {
        // This method is called by HMIChangeListener on the JavaFX Application Thread.
        // We check if the new value is an HmiData object and update the label with its PI_VALUEf.
        if (newValue instanceof HmiData data) {
            Float piValue = data.getPiValuef();

            // Only update the label if there is a PI_VALUEf in the updated data.
            if (piValue != null) {
                String updateText = "Key " + key + " PI_VALUEf: " + piValue;
                System.out.println("TitleController updating label: " + updateText);
                if (testLabel != null) {
                    testLabel.setText(updateText);
                }
            }
        }
    }


    @FXML
    private void switchToSecondary() throws IOException {
        App.setRoot("trainScreen");
    }
}