package org.viewScreens;

import javafx.animation.FadeTransition;
import javafx.animation.ScaleTransition;
import javafx.application.Platform;
import javafx.beans.binding.Bindings;
import javafx.fxml.FXML;
import javafx.scene.control.Button;
import javafx.scene.control.Label;
import javafx.scene.control.ScrollPane;
import javafx.scene.control.TextField;
import javafx.scene.layout.GridPane;
import javafx.util.Duration;
import org.services.DAOService;
import org.viewModels.TitleViewModel;
import org.services.UIStateService;
import org.services.NavigationService;
import java.util.Set;

import org.example.jsonOperator.dto.HmiData;

public class TitleController {

    @FXML
    private GridPane dataGrid;

    @FXML
    private Button sendDataButton;
    @FXML
    private Button goTrainButton; // newly added navigation button
    private TitleViewModel viewModel;
    private Label jsonDisplayLabel;

    private FadeTransition flashingAnimation;

    @FXML
    public void initialize() {
        this.viewModel = new TitleViewModel();
        createJsonDisplayLabel();

        Platform.runLater(() -> {
            populateGrid();
            System.out.println("Initial grid population completed with data binding");
        });

        setupFlashingAnimation();

        if (goTrainButton != null) {
            goTrainButton.setOnAction(e -> NavigationService.getInstance().navigateWhenServerReady("trainScreen"));
        }

        UIStateService.getInstance().waitingForServerProperty().addListener((obs, oldValue, newValue) -> {
            if (newValue) {
                flashingAnimation.play();
                if (sendDataButton != null) sendDataButton.setDisable(true);
                if (goTrainButton != null) goTrainButton.setDisable(true);
            } else {
                flashingAnimation.stop();
                if (sendDataButton != null) {
                    sendDataButton.setDisable(false);
                    sendDataButton.setStyle("");
                }
                if (goTrainButton != null) goTrainButton.setDisable(false);
            }
        });
    }

    private void setupFlashingAnimation() {
        flashingAnimation = new FadeTransition(Duration.seconds(0.5));
        flashingAnimation.setFromValue(1.0);
        flashingAnimation.setToValue(0.5);
        flashingAnimation.setCycleCount(FadeTransition.INDEFINITE);
        flashingAnimation.setAutoReverse(true);
    }

    private void createJsonDisplayLabel() {
        jsonDisplayLabel = new Label();
        jsonDisplayLabel.textProperty().bind(viewModel.jsonStringProperty());
        jsonDisplayLabel.setStyle(
                "-fx-font-family: 'Courier New', monospace;" +
                        "-fx-font-size: 12px;" +
                        "-fx-background-color: #f4f4f4;" +
                        "-fx-border-color: #cccccc;" +
                        "-fx-border-width: 1px;" +
                        "-fx-padding: 10px;" +
                        "-fx-wrap-text: true;"
        );

        jsonDisplayLabel.setMaxWidth(Double.MAX_VALUE);
        jsonDisplayLabel.setPrefHeight(100);

        ScrollPane scrollPane = new ScrollPane(jsonDisplayLabel);
        scrollPane.setFitToWidth(true);
        scrollPane.setPrefHeight(120);
        scrollPane.setStyle("-fx-background-color: transparent;");

        Label jsonTitle = new Label("JSON Updates Being Sent:");
        jsonTitle.setStyle("-fx-font-weight: bold; -fx-font-size: 14px; -fx-text-fill: #2c3e50;");

        dataGrid.add(jsonTitle, 0, 0, 12, 1);
        dataGrid.add(scrollPane, 0, 1, 12, 1);
    }

    private void populateGrid() {
        System.out.println("populateGrid() called with data binding");

        // Clear existing content but preserve JSON display
        dataGrid.getChildren().removeIf(node -> {
            Integer rowIndex = GridPane.getRowIndex(node);
            return rowIndex == null || rowIndex > 1;
        });

        int gridRow = 2;
        int itemCount = 0;

        for (TitleViewModel.HmiDataViewModel dataViewModel : viewModel.getHmiDataList()) {
            itemCount++;

            // Create bound labels that automatically update
            Label tagLabel = createBoundLabel("TAG: ", dataViewModel.tagProperty());
            Label hmiValueiLabel = createBoundLabel("HMI_VALUEi: ", dataViewModel.hmiValueiProperty().asString());
            Label hmiValuebLabel = createBoundLabel("HMI_VALUEb: ", dataViewModel.hmiValuebProperty().asString());
            Label piValuefLabel = createBoundLabel("PI_VALUEf: ", dataViewModel.piValuefProperty().asString());
            Label piValuebLabel = createBoundLabel("PI_VALUEb: ", dataViewModel.piValuebProperty().asString());
            Label hmiReadiLabel = createBoundLabel("HMI_READi: ", dataViewModel.hmiReadiProperty().asString());

            // Apply dynamic styling
            applyDynamicStyling(tagLabel, hmiValuebLabel, piValuebLabel, hmiReadiLabel, dataViewModel);

            // Create interactive buttons
            Button toggleHmiValueb = createStyledButton("Toggle HMI_VALUEb", "#3498db");
            toggleHmiValueb.setOnAction(e -> {
                updateHmiValueb(dataViewModel);
                animateButton(toggleHmiValueb);
            });

            Button togglePiValueb = createStyledButton("Toggle PI_VALUEb", "#9b59b6");
            togglePiValueb.setOnAction(e -> {
                updatePiValueb(dataViewModel);
                animateButton(togglePiValueb);
            });

            TextField hmiValueiField = createStyledTextField("New HMI_VALUEi");
            Button updateHmiValuei = createStyledButton("Update i", "#e74c3c");
            updateHmiValuei.setOnAction(e -> {
                try {
                    Integer newValue = Integer.parseInt(hmiValueiField.getText());
                    updateHmiValuei(dataViewModel, newValue);
                    hmiValueiField.clear();
                    animateButton(updateHmiValuei);
                    flashField(hmiValueiField, "#27ae60");
                } catch (NumberFormatException ex) {
                    flashField(hmiValueiField, "#e74c3c");
                }
            });

            TextField piValuefField = createStyledTextField("New PI_VALUEf");
            Button updatePiValuef = createStyledButton("Update f", "#f39c12");
            updatePiValuef.setOnAction(e -> {
                try {
                    Float newValue = Float.parseFloat(piValuefField.getText());
                    updatePiValuef(dataViewModel, newValue);
                    piValuefField.clear();
                    animateButton(updatePiValuef);
                    flashField(piValuefField, "#27ae60");
                } catch (NumberFormatException ex) {
                    flashField(piValuefField, "#e74c3c");
                }
            });

            // Add to grid
            dataGrid.add(tagLabel, 0, gridRow);
            dataGrid.add(hmiValueiLabel, 1, gridRow);
            dataGrid.add(hmiValuebLabel, 2, gridRow);
            dataGrid.add(piValuefLabel, 3, gridRow);
            dataGrid.add(piValuebLabel, 4, gridRow);
            dataGrid.add(hmiReadiLabel, 5, gridRow);
            dataGrid.add(toggleHmiValueb, 6, gridRow);
            dataGrid.add(togglePiValueb, 7, gridRow);
            dataGrid.add(hmiValueiField, 8, gridRow);
            dataGrid.add(updateHmiValuei, 9, gridRow);
            dataGrid.add(piValuefField, 10, gridRow);
            dataGrid.add(updatePiValuef, 11, gridRow);

            gridRow++;
        }

        System.out.println("Grid populated with " + itemCount + " bound items");
    }

    private Label createBoundLabel(String prefix, javafx.beans.value.ObservableValue<?> property) {
        Label label = new Label();
        label.textProperty().bind(Bindings.concat(prefix, property));
        label.setStyle("-fx-padding: 3px; -fx-background-radius: 3px;");
        return label;
    }

    private void applyDynamicStyling(Label tagLabel, Label hmiValuebLabel, Label piValuebLabel,
                                     Label hmiReadiLabel, TitleViewModel.HmiDataViewModel dataViewModel) {
        tagLabel.setStyle("-fx-font-weight: bold; -fx-text-fill: #2c3e50; -fx-padding: 3px;");

        // Dynamic boolean styling
        hmiValuebLabel.styleProperty().bind(Bindings.createStringBinding(() ->
                        getBooleanLabelStyle(dataViewModel.hmiValuebProperty().get()) + " -fx-padding: 3px;",
                dataViewModel.hmiValuebProperty()));

        piValuebLabel.styleProperty().bind(Bindings.createStringBinding(() ->
                        getBooleanLabelStyle(dataViewModel.piValuebProperty().get()) + " -fx-padding: 3px;",
                dataViewModel.piValuebProperty()));

        // Dynamic readi styling
        hmiReadiLabel.styleProperty().bind(Bindings.createStringBinding(() ->
                        getReadiLabelStyle(dataViewModel.hmiReadiProperty().get()) + " -fx-padding: 3px;",
                dataViewModel.hmiReadiProperty()));
    }

    private void updateHmiValueb(TitleViewModel.HmiDataViewModel dataViewModel) {
        HmiData data = DAOService.getInstance().getHmiDataMap().get(dataViewModel.getKey());
        if (data != null) {
            UIStateService.getInstance().markPending(Set.of(dataViewModel.getKey()));
            Boolean newVal = !dataViewModel.hmiValuebProperty().get();
            data.setHmiValueb(newVal);
            data.setHmiReadi(2);
            DAOService.getInstance().getHmiDataMap().put(dataViewModel.getKey(), data);
        }
    }

    private void updatePiValueb(TitleViewModel.HmiDataViewModel dataViewModel) {
        HmiData data = DAOService.getInstance().getHmiDataMap().get(dataViewModel.getKey());
        if (data != null) {
            UIStateService.getInstance().markPending(Set.of(dataViewModel.getKey()));
            Boolean newVal = !dataViewModel.piValuebProperty().get();
            data.setPiValueb(newVal);
            data.setHmiReadi(2);
            DAOService.getInstance().getHmiDataMap().put(dataViewModel.getKey(), data);
        }
    }

    private void updateHmiValuei(TitleViewModel.HmiDataViewModel dataViewModel, Integer newValue) {
        HmiData data = DAOService.getInstance().getHmiDataMap().get(dataViewModel.getKey());
        if (data != null) {
            UIStateService.getInstance().markPending(Set.of(dataViewModel.getKey()));
            data.setHmiValuei(newValue);
            data.setHmiReadi(2);
            DAOService.getInstance().getHmiDataMap().put(dataViewModel.getKey(), data);
        }
    }

    private void updatePiValuef(TitleViewModel.HmiDataViewModel dataViewModel, Float newValue) {
        HmiData data = DAOService.getInstance().getHmiDataMap().get(dataViewModel.getKey());
        if (data != null) {
            UIStateService.getInstance().markPending(Set.of(dataViewModel.getKey()));
            data.setPiValuef(newValue);
            data.setHmiReadi(2);
            DAOService.getInstance().getHmiDataMap().put(dataViewModel.getKey(), data);
        }
    }

    // Helper methods (styling and animations)
    private Button createStyledButton(String text, String color) {
        Button button = new Button(text);
        button.setStyle(String.format(
                "-fx-background-color: %s; -fx-text-fill: white; -fx-font-weight: bold; " +
                        "-fx-background-radius: 5px; -fx-padding: 5px 10px; -fx-cursor: hand;", color));
        return button;
    }

    private TextField createStyledTextField(String promptText) {
        TextField field = new TextField();
        field.setPromptText(promptText);
        field.setStyle("-fx-border-color: #bdc3c7; -fx-border-radius: 3px; -fx-padding: 3px;");
        return field;
    }

    private String getBooleanLabelStyle(Boolean value) {
        return value ? "-fx-text-fill: #27ae60; -fx-font-weight: bold;" : "-fx-text-fill: #e74c3c; -fx-font-weight: bold;";
    }

    private String getReadiLabelStyle(Integer value) {
        if (value == null || value == 0) return "-fx-text-fill: #95a5a6;";
        return "-fx-text-fill: #f39c12; -fx-font-weight: bold; -fx-background-color: #fff3cd; -fx-background-radius: 3px;";
    }

    private void animateButton(Button button) {
        ScaleTransition scale = new ScaleTransition(Duration.millis(100), button);
        scale.setFromX(1.0);
        scale.setFromY(1.0);
        scale.setToX(0.95);
        scale.setToY(0.95);
        scale.setAutoReverse(true);
        scale.setCycleCount(2);
        scale.play();
    }

    private void flashField(TextField field, String color) {
        String originalStyle = field.getStyle();
        field.setStyle("-fx-border-color: " + color + "; -fx-border-width: 2px; -fx-border-radius: 3px; -fx-padding: 3px;");

        FadeTransition flash = new FadeTransition(Duration.millis(300), field);
        flash.setFromValue(0.7);
        flash.setToValue(1.0);
        flash.setAutoReverse(true);
        flash.setCycleCount(2);
        flash.setOnFinished(e -> field.setStyle(originalStyle));
        flash.play();
    }


    @FXML
    private void switchToSecondary() {
        NavigationService.getInstance().navigateWhenServerReady("trainScreen");
    }
}