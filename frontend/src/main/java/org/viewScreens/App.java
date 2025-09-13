package org.viewScreens;

import javafx.application.Application;
import javafx.fxml.FXMLLoader;
import javafx.scene.Parent;
import javafx.scene.Scene;
import javafx.stage.Stage;
import org.example.Client.ClientFactory;

import java.io.IOException;

/**
 * JavaFX App
 */
public class App extends Application {

    private static Scene scene;

    @Override
    public void start(Stage stage) throws IOException {
        scene = new Scene(loadFXML("title"), 1920, 1080);
        stage.setScene(scene);
        stage.show();
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