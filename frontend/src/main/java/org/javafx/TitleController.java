package org.javafx;

import java.io.IOException;
import javafx.fxml.FXML;

public class TitleController {

    @FXML
    private void switchToSecondary() throws IOException {
        App.setRoot("trainScreen");
    }
}
