package org.viewScreens;

import javafx.beans.property.BooleanProperty;
import javafx.fxml.FXML;
import javafx.scene.control.Button;
import javafx.scene.control.Label;
import javafx.scene.shape.Rectangle;
import org.services.NavigationService;
import org.services.UIStateService;
import org.viewModels.TrainViewModel;

import java.io.IOException;
import java.util.List;

public class TrainController {

    // ViewModel
    private TrainViewModel viewModel;

    // FXML UI Components - Switch Buttons
    @FXML private Button HMI_SWTICH1ABb; // keep typo to match FXML
    @FXML private Button HMI_Switch2b, HMI_Switch3b, HMI_Switch4b, HMI_Switch5ABb, HMI_Switch6ABb;
    // Navigation / other buttons
    @FXML private Button TitleButton, TramButton, UtilitiesButton;
    @FXML private Button Whistle, Bell, Horn;

    // Speed labels
    @FXML private Label RR1ABspeed_HMI, RR1CDspeed_HMI, RR2ABspeed_HMI;

    // Switch 1 Rectangles (True path: T0,T1) (False path: F0,F1,F2)
    @FXML private Rectangle HMI_Switch1ABbT0, HMI_Switch1ABbT1;
    @FXML private Rectangle HMI_Switch1ABbF0, HMI_Switch1ABbF1, HMI_Switch1ABbF2;

    // Switch 2 Rectangles (True: T) (False: F0,F1)
    @FXML private Rectangle HMI_Switch2bT;
    @FXML private Rectangle HMI_Switch2bF0, HMI_Switch2bF1;

    // Switch 3 Rectangles (True: T) (False: F0,F1)
    @FXML private Rectangle HMI_Switch3bT;
    @FXML private Rectangle HMI_Switch3bF0, HMI_Switch3bF1;

    // Switch 4 Rectangles (True: T) (False: F0,F1)
    @FXML private Rectangle HMI_Switch4bT;
    @FXML private Rectangle HMI_Switch4bF0, HMI_Switch4bF1;

    // Switch 5 Rectangles (True: T0,T1) (False: F0,F1,F2)
    @FXML private Rectangle HMI_Switch5ABbT0, HMI_Switch5ABbT1, HMI_Switch5ABbT2;
    @FXML private Rectangle HMI_Switch5ABbF0, HMI_Switch5ABbF1;

    // Switch 6 Rectangles (True: T0,T1) (False: F0,F1,F2)
    @FXML private Rectangle HMI_Switch6ABbT0, HMI_Switch6ABbT1;
    @FXML private Rectangle HMI_Switch6ABbF0, HMI_Switch6ABbF1, HMI_Switch6ABbF2;

    @FXML
    private void initialize() {
        this.viewModel = new TrainViewModel();

//      TODO: Test the speeds
        // Bind speed labels
        RR1ABspeed_HMI.textProperty().bind(viewModel.rr1abSpeedProperty());
        RR1CDspeed_HMI.textProperty().bind(viewModel.rr1cdSpeedProperty());
        RR2ABspeed_HMI.textProperty().bind(viewModel.rr2abSpeedProperty());

//        TODO: Test this as well.
//           Implement the button for diesel vs horn
//            Implement sounds
        // Bind sound control visibility
        Horn.visibleProperty().bind(viewModel.hornVisibleProperty());
        Whistle.visibleProperty().bind(viewModel.whistleVisibleProperty());
        Bell.visibleProperty().bind(viewModel.bellVisibleProperty());

        // Navigation button action wiring
        if (TitleButton != null) {
            TitleButton.setOnAction(e -> NavigationService.getInstance().navigateWhenServerReady("title"));
        }
        
        // Bind sound control actions (server ACK controls final state)
        Horn.setOnAction(e -> viewModel.toggleHmiAction("HMI_RRHornb"));
        Whistle.setOnAction(e -> viewModel.toggleHmiAction("HMI_RRWhistleb"));
        Bell.setOnAction(e -> viewModel.toggleHmiAction("HMI_RRBellb"));

        // Wire switches: rectangles show state only AFTER server ACK updates PI_VALUEb
        bindSwitchComplex(
                "HMI_Switch1ABb",
                HMI_SWTICH1ABb,
                new Rectangle[]{HMI_Switch1ABbT0, HMI_Switch1ABbT1},
                new Rectangle[]{HMI_Switch1ABbF0, HMI_Switch1ABbF1, HMI_Switch1ABbF2}
        );
        bindSwitchComplex(
                "HMI_Switch2RR3b",
                HMI_Switch2b,
                new Rectangle[]{HMI_Switch2bT},
                new Rectangle[]{HMI_Switch2bF0, HMI_Switch2bF1}
        );
        bindSwitchComplex(
                "HMI_Switch3RR4b",
                HMI_Switch3b,
                new Rectangle[]{HMI_Switch3bT},
                new Rectangle[]{HMI_Switch3bF0, HMI_Switch3bF1}
        );
        bindSwitchComplex(
                "HMI_Switch4RR3b",
                HMI_Switch4b,
                new Rectangle[]{HMI_Switch4bT},
                new Rectangle[]{HMI_Switch4bF0, HMI_Switch4bF1}
        );
        bindSwitchComplex(
                "HMI_Switch5ABb",
                HMI_Switch5ABb,
                new Rectangle[]{HMI_Switch5ABbT0, HMI_Switch5ABbT1, HMI_Switch5ABbT2},
                new Rectangle[]{HMI_Switch5ABbF0, HMI_Switch5ABbF1}
        );
        bindSwitchComplex(
                "HMI_Switch6ABb",
                HMI_Switch6ABb,
                new Rectangle[]{HMI_Switch6ABbT0, HMI_Switch6ABbT1},
                new Rectangle[]{HMI_Switch6ABbF0, HMI_Switch6ABbF1, HMI_Switch6ABbF2}
        );

        // Disable switch buttons while waiting for server ACK to avoid spamming
        UIStateService.getInstance().waitingForServerProperty().addListener((obs, oldVal, waiting) -> {
            boolean disable = waiting;
            List.of(HMI_SWTICH1ABb, HMI_Switch2b, HMI_Switch3b, HMI_Switch4b, HMI_Switch5ABb, HMI_Switch6ABb)
                    .forEach(b -> { if (b != null) b.setDisable(disable); });
        });

        System.out.println("[TrainController] Initialized. WaitingForServer=" + UIStateService.getInstance().isWaitingForServer());
    }

    private void bindSwitchComplex(String tag, Button button, Rectangle[] trueRects, Rectangle[] falseRects) {
        if (button == null) return;
        BooleanProperty stateProp = viewModel.getSwitchStateProperty(tag);
        if (stateProp == null) {
            System.err.println("[TrainController] No state property for tag=" + tag);
            return;
        }
        // Action triggers view model toggle; UI rectangles only change upon backend ACK updating PI_VALUEb
        button.setOnAction(e -> viewModel.toggleSwitch(tag));

        if (trueRects != null) {
            for (Rectangle r : trueRects) if (r != null) r.visibleProperty().bind(stateProp);
        }
        if (falseRects != null) {
            for (Rectangle r : falseRects) if (r != null) r.visibleProperty().bind(stateProp.not());
        }
    }

    @FXML
    private void switchToTitle() throws IOException {
        NavigationService.getInstance().navigateWhenServerReady("title");
    }
}