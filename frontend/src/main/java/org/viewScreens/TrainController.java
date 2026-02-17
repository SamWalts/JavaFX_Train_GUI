package org.viewScreens;

import javafx.animation.KeyFrame;
import javafx.animation.Timeline;
import javafx.application.Platform;
import javafx.beans.property.BooleanProperty;
import javafx.beans.value.ChangeListener;
import javafx.beans.value.ObservableValue;
import javafx.fxml.FXML;
import javafx.scene.Scene;
import javafx.scene.control.Button;
import javafx.scene.control.Label;
import javafx.scene.layout.AnchorPane;
import javafx.scene.layout.StackPane;
import javafx.scene.shape.Rectangle;
import org.services.NavigationService;
import org.services.ResponsiveHelper;
import org.services.UIStateService;
import org.viewModels.TrainViewModel;

import java.io.IOException;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

import static javafx.util.Duration.millis;

/**
 * Controller for the train screen.
 *
 * <p>The track-diagram layout uses absolute positioning inside an
 * {@link AnchorPane} designed at 1920×1080.  To support arbitrary
 * screen sizes the controller wraps this pane with a
 * {@link javafx.scene.transform.Scale} transform supplied by
 * {@link ResponsiveHelper#applyContentScaling}, which is applied
 * once the scene is available.</p>
 */
public class TrainController {

    // ViewModel
    private TrainViewModel viewModel;

    // Scaling wrapper (from FXML)
    @FXML private StackPane scalingWrapper;
    @FXML private AnchorPane trainContent;

    // FXML UI Components - Switch Buttons
    @FXML private Button HMI_SWTICH1ABb; // keep typo to match FXML
    @FXML private Button HMI_Switch2b, HMI_Switch3b, HMI_Switch4b, HMI_Switch5ABb, HMI_Switch6ABb, HMI_Switch7ABb, HMI_Switch8b;
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

    // Switch 7 True path rectangles (match FXML ids: HMI_Switch7bT01, HMI_Switch7bT02)
    @FXML
    private Rectangle HMI_Switch7bT01, HMI_Switch7bT02;

    // Switch 8 True path rectangles
    @FXML
    private Rectangle HMI_Switch8bT02, HMI_Switch8bT01;

    // Map to track active flashing animations and original styles per button
    private final Map<Button, Timeline> flashingTimelines = new HashMap<>();
    private final Map<Button, String> originalStyles = new HashMap<>();

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

        // Make the overlay switch buttons visually invisible but still clickable
        makeOverlayInvisible(HMI_SWTICH1ABb);
        makeOverlayInvisible(HMI_Switch2b);
        makeOverlayInvisible(HMI_Switch3b);
        makeOverlayInvisible(HMI_Switch4b);
        makeOverlayInvisible(HMI_Switch5ABb);
        makeOverlayInvisible(HMI_Switch6ABb);
        makeOverlayInvisible(HMI_Switch7ABb);
        makeOverlayInvisible(HMI_Switch8b);

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
        bindSwitchComplex("HMI_Switch7ABb",
                HMI_Switch7ABb,
                new Rectangle[]{HMI_Switch7bT01, HMI_Switch7bT02},
                null);
        bindSwitchComplex("HMI_Switch8ABb",
                HMI_Switch8b,
                new Rectangle[]{HMI_Switch8bT01, HMI_Switch8bT02},
                null);

        // Disable switch buttons while waiting for server ACK to avoid spamming
        UIStateService.getInstance().waitingForServerProperty().addListener((obs, oldVal, waiting) -> {
            boolean disable = waiting;
            List.of(HMI_SWTICH1ABb, HMI_Switch2b, HMI_Switch3b, HMI_Switch4b, HMI_Switch5ABb, HMI_Switch6ABb, HMI_Switch7ABb, HMI_Switch8b)
                    .forEach(b -> { if (b != null) b.setDisable(disable); });
        });

        // Apply responsive scaling once the scene is available
        Platform.runLater(this::applyResponsiveScaling);

        System.out.println("[TrainController] Initialized. WaitingForServer=" + UIStateService.getInstance().isWaitingForServer());
    }

    /**
     * Applies uniform content scaling to the train layout so the fixed-position
     * AnchorPane fits the current window size. Called once after the scene is set.
     */
    private void applyResponsiveScaling() {
        if (trainContent == null) return;
        Scene scene = trainContent.getScene();
        if (scene == null) {
            // Scene may not yet be attached; re-schedule
            trainContent.sceneProperty().addListener((obs, oldScene, newScene) -> {
                if (newScene != null) {
                    ResponsiveHelper.applyContentScaling(trainContent, newScene,
                            ResponsiveHelper.DESIGN_WIDTH, ResponsiveHelper.DESIGN_HEIGHT);
                }
            });
        } else {
            ResponsiveHelper.applyContentScaling(trainContent, scene,
                    ResponsiveHelper.DESIGN_WIDTH, ResponsiveHelper.DESIGN_HEIGHT);
        }
    }

    private void bindSwitchComplex(String tag, Button button, Rectangle[] trueRects, Rectangle[] falseRects) {
        if (button == null) return;
        BooleanProperty stateProp = viewModel.getSwitchStateProperty(tag);
        if (stateProp == null) {
            System.err.println("[TrainController] No state property for tag=" + tag);
            return;
        }
        // Action triggers view model toggle; UI rectangles only change upon backend ACK updating PI_VALUEb
        button.setOnAction(e -> {
            boolean expectedNewState = !stateProp.get();
            startFlashing(button);
            // Holder to allow cross-referencing listeners
            final ChangeListener<Boolean>[] waitingRef = new ChangeListener[1];
            // Listener to stop on specific state change (ACK reflected in state)
            ChangeListener<Boolean> stateListener = new ChangeListener<>() {
                @Override
                public void changed(ObservableValue<? extends Boolean> obs, Boolean oldVal, Boolean newVal) {
                    if (newVal != null && newVal == expectedNewState) {
                        stopFlashing(button);
                        stateProp.removeListener(this);
                        // Also remove the global waiting listener if present
                        if (waitingRef[0] != null) {
                            UIStateService.getInstance().waitingForServerProperty().removeListener(waitingRef[0]);
                            waitingRef[0] = null;
                        }
                    }
                }
            };
            // Listener to stop on global waiting cleared (all ACKed)
            ChangeListener<Boolean> waitingListener = new ChangeListener<>() {
                @Override
                public void changed(ObservableValue<? extends Boolean> obs, Boolean oldVal, Boolean waiting) {
                    if (waiting != null && !waiting) {
                        stopFlashing(button);
                        UIStateService.getInstance().waitingForServerProperty().removeListener(this);
                        stateProp.removeListener(stateListener);
                    }
                }
            };
            waitingRef[0] = waitingListener;
            stateProp.addListener(stateListener);
            UIStateService.getInstance().waitingForServerProperty().addListener(waitingListener);
            viewModel.toggleSwitch(tag);
        });

        if (trueRects != null) {
            for (Rectangle r : trueRects) if (r != null) r.visibleProperty().bind(stateProp);
        }
        if (falseRects != null) {
            for (Rectangle r : falseRects) if (r != null) r.visibleProperty().bind(stateProp.not());
        }
    }

    private void makeOverlayInvisible(Button b) {
        if (b == null) return;
        originalStyles.putIfAbsent(b, b.getStyle());
        b.getStyleClass().add("switch-overlay");
        b.setFocusTraversable(false);
    }

    private void startFlashing(Button b) {
        if (b == null) return;
        // If already flashing, do nothing
        Timeline existing = flashingTimelines.get(b);
        if (existing != null) {
            if (existing.getStatus() == Timeline.Status.RUNNING) return;
        }
        originalStyles.putIfAbsent(b, b.getStyle());
        Timeline tl = new Timeline(
                new KeyFrame(millis(0), ae -> applyFlashStyle(b, true)),
                new KeyFrame(millis(500), ae -> applyFlashStyle(b, false))
        );
        tl.setCycleCount(Timeline.INDEFINITE);
        flashingTimelines.put(b, tl);
        tl.play();
    }

    private void applyFlashStyle(Button b, boolean on) {
        if (on) {
            b.getStyleClass().remove("switch-overlay");
            b.getStyleClass().add("switch-overlay-flash");
        } else {
            b.getStyleClass().remove("switch-overlay-flash");
            b.getStyleClass().add("switch-overlay");
        }
    }

    private void stopFlashing(Button b) {
        if (b == null) return;
        Timeline tl = flashingTimelines.remove(b);
        if (tl != null) {
            tl.stop();
        }
        b.getStyleClass().remove("switch-overlay-flash");
        if (!b.getStyleClass().contains("switch-overlay")) {
            b.getStyleClass().add("switch-overlay");
        }
    }

    @FXML
    private void switchToTitle() throws IOException {
        NavigationService.getInstance().navigateWhenServerReady("title");
    }
}
