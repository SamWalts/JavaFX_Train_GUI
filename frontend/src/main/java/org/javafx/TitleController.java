package org.javafx;

import javafx.fxml.FXML;
import java.io.IOException;
import javafx.scene.control.Button;
import javafx.scene.control.Label;
import javafx.scene.control.TextField;
import javafx.scene.layout.GridPane;
import org.example.jsonOperator.dto.HmiData;
import org.services.DAOService;

public class TitleController {

    @FXML
    private GridPane dataGrid;

    @FXML
    public void initialize() {
        for (int i = 1; i <= 80; i++) {
            final int key = i;
            HmiData data = DAOService.getInstance().getHmiDataMap().get(String.valueOf(key));
            if (data == null) continue;

            // Existing labels
            Label tagLabel = new Label("TAG: " + data.getTag());
            Label hmiValueiLabel = new Label("HMI_VALUEi: " + data.getHmiValuei());
            Label hmiValuebLabel = new Label("HMI_VALUEb: " + data.getHmiValueb());
            Label piValuefLabel = new Label("PI_VALUEf: " + data.getPiValuef());
            Label piValuebLabel = new Label("PI_VALUEb: " + data.getPiValueb());
            Label hmiReadiLabel = new Label("HMI_READi: " + data.getHmiReadi());

            // Toggle buttons for boolean values
            Button toggleHmiValueb = new Button("Toggle HMI_VALUEb");
            toggleHmiValueb.setOnAction(e -> {
                Boolean currentVal = data.getHmiValueb();
                data.setHmiValueb(currentVal == null ? true : !currentVal);
                data.setHmiReadi(1);
                DAOService.getInstance().getHmiDataMap().put(String.valueOf(key), data);
                hmiValuebLabel.setText("HMI_VALUEb: " + data.getHmiValueb());
                hmiReadiLabel.setText("HMI_READi: " + data.getHmiReadi());
            });

            Button togglePiValueb = new Button("Toggle PI_VALUEb");
            togglePiValueb.setOnAction(e -> {
                Boolean currentVal = data.getPiValueb();
                data.setPiValueb(currentVal == null ? true : !currentVal);
                data.setHmiReadi(1);
                DAOService.getInstance().getHmiDataMap().put(String.valueOf(key), data);
                piValuebLabel.setText("PI_VALUEb: " + data.getPiValueb());
                hmiReadiLabel.setText("HMI_READi: " + data.getHmiReadi());
            });

            // Text fields to change integer and float values
            TextField hmiValueiField = new TextField();
            hmiValueiField.setPromptText("New HMI_VALUEi");
            Button updateHmiValuei = new Button("Update i");
            updateHmiValuei.setOnAction(e -> {
                try {
                    int newValue = Integer.parseInt(hmiValueiField.getText());
                    data.setHmiValuei(newValue);
                    data.setHmiReadi(1);
                    DAOService.getInstance().getHmiDataMap().put(String.valueOf(key), data);
                    hmiValueiLabel.setText("HMI_VALUEi: " + data.getHmiValuei());
                    hmiReadiLabel.setText("HMI_READi: " + data.getHmiReadi());
                } catch (NumberFormatException ex) {
                    hmiValueiField.setText("Invalid number");
                }
            });

            TextField piValuefField = new TextField();
            piValuefField.setPromptText("New PI_VALUEf");
            Button updatePiValuef = new Button("Update f");
            updatePiValuef.setOnAction(e -> {
                try {
                    float newValue = Float.parseFloat(piValuefField.getText());
                    data.setPiValuef(newValue);
                    data.setHmiReadi(1);
                    DAOService.getInstance().getHmiDataMap().put(String.valueOf(key), data);
                    piValuefLabel.setText("PI_VALUEf: " + data.getPiValuef());
                    hmiReadiLabel.setText("HMI_READi: " + data.getHmiReadi());
                } catch (NumberFormatException ex) {
                    piValuefField.setText("Invalid number");
                }
            });

            // Add existing labels
            dataGrid.add(tagLabel, 0, key);
            dataGrid.add(hmiValueiLabel, 1, key);
            dataGrid.add(hmiValuebLabel, 2, key);
            dataGrid.add(piValuefLabel, 3, key);
            dataGrid.add(piValuebLabel, 4, key);
            dataGrid.add(hmiReadiLabel, 5, key);

//          Add the controls for the row.
            dataGrid.add(toggleHmiValueb, 6, key);
            dataGrid.add(togglePiValueb, 7, key);
            dataGrid.add(hmiValueiField, 8, key);
            dataGrid.add(updateHmiValuei, 9, key);
            dataGrid.add(piValuefField, 10, key);
            dataGrid.add(updatePiValuef, 11, key);
        }
    }

    @FXML
    private void switchToSecondary() throws IOException {
        App.setRoot("trainScreen");
    }
}