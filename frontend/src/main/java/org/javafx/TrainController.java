package org.javafx;

import java.io.IOException;
import javafx.fxml.FXML;

public class TrainController {

    @FXML
    private void switchToPrimary() throws IOException {
        App.setRoot("primary");
    }
}