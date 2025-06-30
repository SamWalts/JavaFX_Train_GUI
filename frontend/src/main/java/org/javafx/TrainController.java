package org.javafx;

import javafx.beans.property.BooleanProperty;
import javafx.fxml.FXML;
import javafx.scene.control.Button;
import javafx.scene.control.Label;
import javafx.scene.shape.Rectangle;
import org.viewModels.TrainViewModel;

import java.io.IOException;

public class TrainController {

    // ViewModel
    private TrainViewModel viewModel;

    // FXML UI Components
    @FXML private Button HMI_SWTICH1ABb, HMI_Switch2b, HMI_Switch3b, HMI_Switch4b, HMI_Switch5ABb, HMI_Switch6ABb;
    @FXML private Button TitleButton, TramButton, UtilitiesButton;
    @FXML private Button Whistle, Bell, Horn;

    @FXML private Rectangle HMI_Switch1ABbT1, HMI_Switch1ABbF2;
    @FXML private Rectangle HMI_Switch2bT, HMI_Switch2bF1;
    @FXML private Rectangle HMI_Switch3bT, HMI_Switch3bF1;
    @FXML private Rectangle HMI_Switch4bT, HMI_Switch4bF1;
    @FXML private Rectangle HMI_Switch5ABbT1, HMI_SWITCH5ABbF2;
    @FXML private Rectangle HMI_Switch6ABbT1, HMI_SWITCH6ABbF2;

    @FXML private Label RR1ABspeed_HMI, RR1CDspeed_HMI, RR2ABspeed_HMI;

    @FXML
    private void initialize() {
        this.viewModel = new TrainViewModel();

        // Bind speed labels
        RR1ABspeed_HMI.textProperty().bind(viewModel.rr1abSpeedProperty());
        RR1CDspeed_HMI.textProperty().bind(viewModel.rr1cdSpeedProperty());
        RR2ABspeed_HMI.textProperty().bind(viewModel.rr2abSpeedProperty());

        // Bind sound control visibility
        Horn.visibleProperty().bind(viewModel.hornVisibleProperty());
        Whistle.visibleProperty().bind(viewModel.whistleVisibleProperty());
        Bell.visibleProperty().bind(viewModel.bellVisibleProperty());

        // Bind sound control actions
        Horn.setOnAction(event -> viewModel.toggleHmiAction("HMI_RRHornb"));
        Whistle.setOnAction(event -> viewModel.toggleHmiAction("HMI_RRWhistleb"));
        Bell.setOnAction(event -> viewModel.toggleHmiAction("HMI_RRBellb"));

        // Bind switches
        bindSwitch("HMI_Switch1ABb", HMI_SWTICH1ABb, HMI_Switch1ABbT1, HMI_Switch1ABbF2);
        bindSwitch("HMI_Switch2RR3b", HMI_Switch2b, HMI_Switch2bT, HMI_Switch2bF1);
        bindSwitch("HMI_Switch3RR4b", HMI_Switch3b, HMI_Switch3bT, HMI_Switch3bF1);
        bindSwitch("HMI_Switch4RR3b", HMI_Switch4b, HMI_Switch4bT, HMI_Switch4bF1);
        bindSwitch("HMI_Switch5ABb", HMI_Switch5ABb, HMI_Switch5ABbT1, HMI_SWITCH5ABbF2);
        bindSwitch("HMI_Switch6ABb", HMI_Switch6ABb, HMI_Switch6ABbT1, HMI_SWITCH6ABbF2);

        System.out.println("TrainController initialized and bound to TrainViewModel.");
    }

    /**
     * Helper method to bind a switch's UI components to the ViewModel.
     * @param tag The data tag for the switch.
     * @param button The button that toggles the switch.
     * @param thrownRect The rectangle visible when the switch is thrown (true).
     * @param closedRect The rectangle visible when the switch is closed (false).
     */
    private void bindSwitch(String tag, Button button, Rectangle thrownRect, Rectangle closedRect) {
        if (button != null) {
            // Set the action to call the ViewModel's logic
            button.setOnAction(event -> viewModel.toggleSwitch(tag));

            // Bind the visibility of the state rectangles to the ViewModel's property
            BooleanProperty switchState = viewModel.getSwitchStateProperty(tag);
            if (switchState != null) {
                if (thrownRect != null) thrownRect.visibleProperty().bind(switchState);
                if (closedRect != null) closedRect.visibleProperty().bind(switchState.not());
            }
        }
    }

    @FXML
    private void switchToTitle() throws IOException {
        App.setRoot("title");
    }
}