package org.viewScreens;

import javafx.application.Application;
import javafx.fxml.FXMLLoader;
import javafx.scene.Parent;
import javafx.scene.Scene;
import javafx.stage.Stage;
import org.example.Client.ClientFactory;
import org.services.PythonServerManager;

import java.io.IOException;
import java.util.logging.Level;
import java.util.logging.Logger;

/**
 * JavaFX App
 */
public class App extends Application {

    private static final Logger LOGGER = Logger.getLogger(App.class.getName());
    private static Scene scene;

    @Override
    public void start(Stage stage) throws IOException {
        // Start the Python server before showing the UI
        try {
            PythonServerManager.getInstance().startServer();
            LOGGER.info("Python server started successfully");
        } catch (IOException e) {
            LOGGER.log(Level.SEVERE, "Failed to start Python server", e);
            // Continue with the application even if server fails to start
        }
        
        scene = new Scene(loadFXML("title"), 1920, 1080);
        stage.setScene(scene);
        stage.show();
    }

    @Override
    public void stop() throws Exception {
        // Stop the Python server when the application is closing
        try {
            PythonServerManager.getInstance().stopServer();
            LOGGER.info("Python server stopped successfully");
        } catch (Exception e) {
            LOGGER.log(Level.WARNING, "Error stopping Python server", e);
        }
        super.stop();
    }

    public static void setRoot(String fxml) throws IOException {
        scene.setRoot(loadFXML(fxml));
    }

    private static Parent loadFXML(String fxml) throws IOException {
        FXMLLoader fxmlLoader = new FXMLLoader(App.class.getResource(fxml + ".fxml"));
        return fxmlLoader.load();
    }

    /**
     * Main method to launch the JavaFX application and start the client controller in a separate thread.
     * With this setup, the client controller can handle server communication while the JavaFX UI runs in the main thread.
     * This allows the client to run concurrently with the JavaFX UI.
     *
     * @param args command line arguments
     */
    public static void main(String[] args) {
        new Thread(() -> {
            try {
                ClientFactory.getClientController();
            } catch (RuntimeException e) {
                e.printStackTrace();
            }
        }).start();
        launch();
    }

}