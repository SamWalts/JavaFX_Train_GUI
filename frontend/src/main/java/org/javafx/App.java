package org.javafx;

import javafx.application.Application;
import javafx.fxml.FXMLLoader;
import javafx.scene.Parent;
import javafx.scene.Scene;
import javafx.stage.Stage;
import org.services.DAOService;

import java.io.IOException;

/**
 * Main application class for the JavaFX frontend.
 * It initializes the application, loads the initial FXML view,
 * and manages the primary stage (window).
 */
public class App extends Application {

    private static Scene scene;

    @Override
    public void start(Stage stage) throws IOException {
        // Initialize the singleton DAOService. This creates the shared data map.
        // The stub file loading from `TestingClassFillTheMap` has been removed.
        // A separate service for communicating with the Python backend should be
        // initialized here to populate and synchronize the data map in DAOService.
        DAOService.getInstance();

        scene = new Scene(loadFXML("title"), 640, 480);
        stage.setScene(scene);
        stage.show();
    }

    static void setRoot(String fxml) throws IOException {
        scene.setRoot(loadFXML(fxml));
    }

    private static Parent loadFXML(String fxml) throws IOException {
        FXMLLoader fxmlLoader = new FXMLLoader(App.class.getResource(fxml + ".fxml"));
        return fxmlLoader.load();
    }

    public static void main(String[] args) {
        launch();
    }
}