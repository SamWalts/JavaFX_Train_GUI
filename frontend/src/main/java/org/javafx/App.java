package org.javafx;

import javafx.application.Application;
import javafx.fxml.FXMLLoader;
import javafx.scene.Parent;
import javafx.scene.Scene;
import javafx.stage.Stage;
import org.example.jsonOperator.dao.HMIJSONDAOStub;
import org.example.jsonOperator.dao.ListenerConcurrentMap;
import org.example.jsonOperator.dto.HmiData;
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
        // Load the FXML
        FXMLLoader fxmlLoader = new FXMLLoader(App.class.getResource("title.fxml"));
        scene = new Scene(fxmlLoader.load());

        // Get the controller that implements HMIControllerInterface
        Object controller = fxmlLoader.getController();

        // Get the shared DAO from our service
        HMIJSONDAOStub hmiJsonDao = DAOService.getInstance().getHmiJsonDao();

        // Create the listener
        if (controller instanceof HMIControllerInterface) {
            HMIChangeListener listener = new HMIChangeListener(hmiJsonDao, (HMIControllerInterface)controller);
            System.out.println("HMI Listener initialized");
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

            // If it's our TrainController, create a listener for it
            if (controller instanceof TrainController trainController) {

                // Inject the shared DAO
                trainController.setHmiJsonDao(hmiJsonDao);

                // Create listener for this controller
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