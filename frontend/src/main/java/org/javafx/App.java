package org.javafx;

import javafx.application.Application;
import javafx.fxml.FXMLLoader;
import javafx.scene.Parent;
import javafx.scene.Scene;
import javafx.stage.Stage;
import org.example.jsonOperator.dao.HMIJSONDAOStub;
import org.example.jsonOperator.dao.TestingClassFillTheMap; // Import the loader class
import org.services.DAOService;
import org.services.HMIChangeListener;
import org.services.HMIControllerInterface;

import java.io.IOException;

/**
 * JavaFX App
 */
public class App extends Application {

    private static Scene scene;

    @Override
    public void start(Stage stage) throws IOException {
        // 1. Get the single, shared DAO instance from the service
        HMIJSONDAOStub hmiJsonDao = DAOService.getInstance().getHmiJsonDao();

        // 2. Load the FXML and get the controller
        FXMLLoader fxmlLoader = new FXMLLoader(App.class.getResource("title.fxml"));
        scene = new Scene(fxmlLoader.load());
        Object controller = fxmlLoader.getController();

        // 3. Create the listener and attach it BEFORE data is loaded
        if (controller instanceof HMIControllerInterface) {
            HMIChangeListener listener = new HMIChangeListener(hmiJsonDao, (HMIControllerInterface)controller);
            System.out.println("HMI Listener initialized for TitleController.");
        }

        // 4. Load the data. This will now trigger the listener for each item.
        try {
            TestingClassFillTheMap.loadDataFromJsonFile(hmiJsonDao);
            System.out.println("Successfully requested data load into the shared DAO.");

        } catch (IOException e) {
            System.err.println("Failed to load data from PiHmiDict.json: " + e.getMessage());
        }

        stage.setScene(scene);
        stage.show();
    }

    static void setRoot(String fxml) throws IOException {
        scene.setRoot(loadFXML(fxml));
    }

    private static Parent loadFXML(String fxml) throws IOException {
        FXMLLoader fxmlLoader = new FXMLLoader(App.class.getResource(fxml + ".fxml"));

        // Special handling for train screen
        if (fxml.equals("trainScreen")) {
            // Get the shared DAO instance
            HMIJSONDAOStub hmiJsonDao = DAOService.getInstance().getHmiJsonDao();

            // Get the controller after loading
            Parent root = fxmlLoader.load();
            Object controller = fxmlLoader.getController();
            if (controller instanceof TrainController trainController) {
                // Assuming TrainController has a similar setup
                // trainController.setHmiJsonDao(hmiJsonDao);

                HMIChangeListener listener = new HMIChangeListener(hmiJsonDao, trainController);
                System.out.println("Train HMI Listener initialized");
            }

            return root;
        } else {
            // Normal loading for other screens
            return fxmlLoader.load();
        }
    }

    public static void main(String[] args) {
        launch();
    }

}