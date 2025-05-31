package org.javafx;

import javafx.beans.property.SimpleBooleanProperty;
import javafx.fxml.FXML;
import javafx.scene.control.Button;
import javafx.scene.control.Label;
import javafx.scene.shape.Rectangle;
import org.example.jsonOperator.dao.HMIJSONDAOStub;
import org.services.DAOService;
import org.services.HMIControllerInterface;

import java.io.IOException;
import java.util.Arrays;
import java.util.List;

public class TrainController implements HMIControllerInterface {
    private HMIJSONDAOStub hmiJsonDao;

    @FXML private Button HMI_SWTICH1ABb;
    @FXML private Button HMI_Switch3b;
    @FXML private Button HMI_Switch2b;
    @FXML private Button HMI_Switch4b;
    @FXML private Button HMI_Switch5ABb;
    @FXML private Button HMI_Switch6ABb;
    @FXML private Button TitleButton;
    @FXML private Button TramButton;
    @FXML private Button UtilitiesButton;
    @FXML private Button Whistle;
    @FXML private Button Bell;
    @FXML private Button Horn;

    @FXML private Rectangle HMI_SWITCH5ABbF2;
    @FXML private Rectangle HMI_SWITCH5ABbT1;
    @FXML private Rectangle HMI_SWITCH6ABbF0;
    @FXML private Rectangle HMI_SWITCH6ABbF1;
    @FXML private Rectangle HMI_SWITCH6ABbF2;
    @FXML private Rectangle HMI_SWITCH6ABbT0;
    @FXML private Rectangle HMI_SWITCH6ABbT1;

    @FXML private Rectangle HMI_Switch1ABbF0;
    @FXML private Rectangle HMI_Switch1ABbF1;
    @FXML private Rectangle HMI_Switch1ABbF2;
    @FXML private Rectangle HMI_Switch1ABbT0;
    @FXML private Rectangle HMI_Switch1ABbT1;
    @FXML private Rectangle HMI_Switch2bF0;
    @FXML private Rectangle HMI_Switch2bF1;
    @FXML private Rectangle HMI_Switch2bT;
    @FXML private Rectangle HMI_Switch3bF0;
    @FXML private Rectangle HMI_Switch3bF1;
    @FXML private Rectangle HMI_Switch3bT;
    @FXML private Rectangle HMI_Switch4bF0;
    @FXML private Rectangle HMI_Switch4bF1;
    @FXML private Rectangle HMI_Switch4bT;
    @FXML private Rectangle HMI_Switch5ABbF0;
    @FXML private Rectangle HMI_Switch5ABbF1;
    @FXML private Rectangle HMI_Switch5ABbT0;
    @FXML private Label RR1ABspeed_HMI;
    @FXML private Label RR1CDspeed_HMI;
    @FXML private Label RR2ABspeed_HMI;

    // TODO: This is a test method to check data from backend to frontend
    private void updateSpeedLabels() {
        hmiJsonDao.fetchAll().forEach((key, value) -> {
            if (key.equals("RR1ABspeed")) {
                RR1ABspeed_HMI.setText(String.valueOf(value.getHmiReadi()));
            } else if (key.equals("RR1CDspeed")) {
                RR1CDspeed_HMI.setText(String.valueOf(value.getHmiReadi()));
            } else if (key.equals("RR2ABspeed")) {
                RR2ABspeed_HMI.setText(String.valueOf(value.getHmiReadi()));
            }
        });
    }
    private List<Rectangle> switch1Rectangles;
    private List<Rectangle> switch2Rectangles;
    private List<Rectangle> switch3Rectangles;
    private List<Rectangle> switch4Rectangles;
    private List<Rectangle> switch5Rectangles;
    private List<Rectangle> switch6Rectangles;

    // FIXME: These are test variables. Will delete when DB is implemented
    Boolean isSwitch1ABb = false;
    Boolean isSwitch2b = false;
    Boolean isSwitch3b = false;
    Boolean isSwitch4b = false;
    Boolean isSwitch5ABb = false;
    Boolean isSwitch6ABb = false;

    private SimpleBooleanProperty isDiesel = new SimpleBooleanProperty(true);
    private SimpleBooleanProperty isSteam = new SimpleBooleanProperty(true);

    public TrainController() {
        System.out.println("TrainController FXML constructor called");
    }

    public TrainController(HMIJSONDAOStub hmiJsonDao) {
        this.hmiJsonDao = hmiJsonDao;
        System.out.println("TrainController constructor called with the DAO");
    }

    public HMIJSONDAOStub getHmiJsonDao() {
        return hmiJsonDao;
    }

    public void setHmiJsonDao(HMIJSONDAOStub hmiJsonDao) {
        this.hmiJsonDao = hmiJsonDao;
        System.out.println("DAO injected into controller");
    }

    @Override
    public void onMapUpdate(String key, Object oldValue, Object newValue) {
        System.out.println("TrainController - Map updated: " + key);

        // Update UI elements based on the changes
        if (key.contains("Switch1")) {
            isSwitch1ABb = (newValue != null);  // Assuming null means inactive
            updateSwitchRectangles(switch1Rectangles, isSwitch1ABb);
        } else if (key.contains("Switch2")) {
            isSwitch2b = (newValue != null);
            updateSwitchRectangles(switch2Rectangles, isSwitch2b);
        } else if (key.contains("Switch3")) {
            isSwitch3b = (newValue != null);
            updateSwitchRectangles(switch3Rectangles, isSwitch3b);
        } else if (key.contains("Switch4")) {
            isSwitch4b = (newValue != null);
            updateSwitchRectangles(switch4Rectangles, isSwitch4b);
        } else if (key.contains("Switch5")) {
            isSwitch5ABb = (newValue != null);
            updateSwitchRectangles(switch5Rectangles, isSwitch5ABb);
        } else if (key.contains("Switch6")) {
            isSwitch6ABb = (newValue != null);
            updateSwitchRectangles(switch6Rectangles, isSwitch6ABb);
        }
    }

    @FXML
    private void initialize() {
        if (hmiJsonDao == null) {
            hmiJsonDao = DAOService.getInstance().getHmiJsonDao();
            System.out.println("DAO initialized in TrainController");
        }
        System.out.println("TrainController initialized");
        updateSoundStates();
        updateSpeedLabels();
        isDiesel.addListener((observable, oldValue, newValue) -> {
            Bell.setDisable(newValue);
        });

        Bell.setOnAction(event -> {
            updateSoundStates();
            System.out.println("Bell clicked");
        });

        Horn.setOnAction(event -> {
            updateSoundStates();
            System.out.println("Horn clicked");
        });

        Whistle.setOnAction(event -> {
            updateSoundStates();
            System.out.println("Whistle clicked");
        });

        HMI_SWTICH1ABb.setOnAction(event -> {
            System.out.println("HMI_Switch1ABb clicked");
            handleSwitchButton(HMI_SWTICH1ABb);
        });

        TitleButton.setOnAction(event -> {
            try {
                handleTitleButton();
            } catch (IOException e) {
                throw new RuntimeException(e);
            }
        });

        HMI_Switch2b.setOnAction(event -> {
            System.out.println("HMI_Switch2b clicked");
            handleSwitchButton(HMI_Switch2b);
        });

        HMI_Switch3b.setOnAction(event -> {
            System.out.println("HMI_Switch3b clicked");
            handleSwitchButton(HMI_Switch3b);
        });

        HMI_Switch4b.setOnAction(event -> {
            System.out.println("HMI_Switch4b clicked");
            handleSwitchButton(HMI_Switch4b);
        });

        HMI_Switch5ABb.setOnAction(event -> {
            System.out.println("HMI_Switch5ABb clicked");
            handleSwitchButton(HMI_Switch5ABb);
        });

        HMI_Switch6ABb.setOnAction(event -> {
            System.out.println("HMI_Switch6ABb clicked");
            handleSwitchButton(HMI_Switch6ABb);
        });

        TramButton.setOnAction(event -> {
            try {
                handleTramButton();
            } catch (IOException e) {
                throw new RuntimeException(e);
            }
        });
        UtilitiesButton.setOnAction(event -> {
            try {
                handleUtilitiesButton();
            } catch (IOException e) {
                throw new RuntimeException(e);
            }
        });
        initializeSwitchLists();
    }

    private void initializeSwitchLists() {
        switch1Rectangles = Arrays.asList(
                HMI_Switch1ABbF0,
                HMI_Switch1ABbF1,
                HMI_Switch1ABbF2,
                HMI_Switch1ABbT0,
                HMI_Switch1ABbT1
        );

        switch2Rectangles = Arrays.asList(
                HMI_Switch2bF0,
                HMI_Switch2bF1,
                HMI_Switch2bT
        );

        switch3Rectangles = Arrays.asList(
                HMI_Switch3bF0,
                HMI_Switch3bF1,
                HMI_Switch3bT
        );

        switch4Rectangles = Arrays.asList(
                HMI_Switch4bF0,
                HMI_Switch4bF1,
                HMI_Switch4bT
        );

        switch5Rectangles = Arrays.asList(
                HMI_Switch5ABbF0,
                HMI_Switch5ABbF1,
                HMI_Switch5ABbT0
        );

        switch6Rectangles = Arrays.asList(
                HMI_SWITCH6ABbF0,
                HMI_SWITCH6ABbF1,
                HMI_SWITCH6ABbF2,
                HMI_SWITCH6ABbT0,
                HMI_SWITCH6ABbT1
        );
    }

    private void handleUtilitiesButton() throws IOException {
        System.out.println("Utilities button clicked");
        App.setRoot("utilitiesScreen");
    }

    private void handleTramButton() throws IOException {
        System.out.println("Tram button clicked");
        App.setRoot("tramScreen");
    }

    private void handleTitleButton() throws IOException {
        System.out.println("Title button clicked");
        App.setRoot("title");
    }

    private void handleSwitchButton(Button button) {
        System.out.println("Switch button clicked");
        String buttonId = button.getId();

        switch (buttonId) {
            case "HMI_SWTICH1ABb":
                isSwitch1ABb = !isSwitch1ABb;
                updateSwitchRectangles(switch1Rectangles, isSwitch1ABb);
                break;
            case "HMI_Switch2b":
                isSwitch2b = !isSwitch2b;
                updateSwitchRectangles(switch2Rectangles, isSwitch2b);
                break;
            case "HMI_Switch3b":
                isSwitch3b = !isSwitch3b;
                updateSwitchRectangles(switch3Rectangles, isSwitch3b);
                break;
            case "HMI_Switch4b":
                isSwitch4b = !isSwitch4b;
                updateSwitchRectangles(switch4Rectangles, isSwitch4b);
                break;
            case "HMI_Switch5ABb":
                isSwitch5ABb = !isSwitch5ABb;
                updateSwitchRectangles(switch5Rectangles, isSwitch5ABb);
                break;
            case "HMI_Switch6ABb":
                isSwitch6ABb = !isSwitch6ABb;
                updateSwitchRectangles(switch6Rectangles, isSwitch6ABb);
                break;
            default:
                System.out.println("Unknown button ID: " + buttonId);
        }
    }

    private void updateSwitchRectangles(List<Rectangle> rectangles, boolean isActive) {
        System.out.println("Updating Switch Rectangles");
        if (rectangles == null || rectangles.isEmpty()) {
            System.out.println("No rectangles to update");
            return;
        }

        for (Rectangle rectangle : rectangles) {
            String rectangleId = rectangle.getId();
            if (rectangleId.endsWith("T0") || rectangleId.endsWith("T1") || rectangleId.endsWith("T")) {
                rectangle.setVisible(isActive);
            } else if (rectangleId.contains("F")) {
                rectangle.setVisible(!isActive);
            }
        }
    }

    private void updateSoundStates() {
        Bell.setVisible(!isDiesel.get());
        Bell.setDisable(isDiesel.get());

        Horn.setVisible(isDiesel.get());
        Horn.setDisable(!isDiesel.get());

        Whistle.setVisible(!isDiesel.get());
        Whistle.setDisable(isDiesel.get());
    }
}