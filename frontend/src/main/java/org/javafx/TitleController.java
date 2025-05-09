package org.javafx;

import java.io.IOException;
import javafx.fxml.FXML;
import org.services.HMIControllerInterface;

public class TitleController implements HMIControllerInterface {

    @Override
    public void onMapUpdate(String key, Object oldValue, Object newValue) {
        System.out.println("Map updated: " + key);
        // Update UI elements based on the changes
    }

    @FXML
    private void switchToSecondary() throws IOException {
        App.setRoot("trainScreen");
    }
}