package org.viewScreens;

import javafx.application.Application;
import javafx.fxml.FXMLLoader;
import javafx.geometry.Rectangle2D;
import javafx.scene.Parent;
import javafx.scene.Scene;
import javafx.stage.Screen;
import javafx.stage.Stage;
import org.example.Client.ClientFactory;
import org.services.Cleanable;

import java.io.IOException;
import java.util.Objects;

/**
 * JavaFX App – main entry point for the Train GUI.
 *
 * <p>The application dynamically sizes itself to the primary screen,
 * using 80% of the available width/height so the window is usable on
 * any display. A global CSS stylesheet ({@code styles.css}) is loaded
 * once and shared across all screens.</p>
 *
 * <h3>Extending with a new screen</h3>
 * <ol>
 *   <li>Create a new FXML file under {@code resources/org/viewScreens/}.</li>
 *   <li>Create a matching controller in {@code org.viewScreens}.</li>
 *   <li>Navigate to it via {@link #setRoot(String)} or {@link org.services.NavigationService}.</li>
 *   <li>The global stylesheet and responsive scaling will apply automatically.</li>
 * </ol>
 */
public class App extends Application {

    private static Scene scene;
    private static Object currentController;

    /** Fraction of the primary screen used for the initial window size. */
    private static final double SCREEN_USAGE_FRACTION = 0.80;

    @Override
    public void start(Stage stage) throws IOException {
        // Determine initial window size from the primary display
        Rectangle2D screenBounds = Screen.getPrimary().getVisualBounds();
        double width  = screenBounds.getWidth()  * SCREEN_USAGE_FRACTION;
        double height = screenBounds.getHeight() * SCREEN_USAGE_FRACTION;

        scene = new Scene(loadFXML("title"), width, height);
        scene.getStylesheets().add(
                Objects.requireNonNull(App.class.getResource("styles.css")).toExternalForm());

        stage.setTitle("KEW&J National Railroad (KNRR)");
        stage.setScene(scene);
        stage.show();
    }

    /**
     * Called when the application is stopping.
     * Cleans up all resources to ensure the JVM can exit cleanly.
     */
    @Override
    public void stop() throws Exception {
        System.out.println("Application stopping, cleaning up resources...");

        // Cleanup current controller
        cleanupCurrentController();

        // Shutdown the DAOService (which shuts down the ListenerConcurrentMap scheduler)
        try {
            org.services.DAOService.getInstance().shutdown();
        } catch (Exception e) {
            System.err.println("Error shutting down DAOService: " + e.getMessage());
        }

        // Shutdown the client controller
        try {
            ClientFactory.shutdown();
        } catch (Exception e) {
            System.err.println("Error shutting down ClientFactory: " + e.getMessage());
        }

        super.stop();
        System.out.println("Cleanup complete, application exiting.");
    }

    /**
     * Returns the current application scene.
     * Controllers can use this to obtain scene dimensions for responsive binding.
     *
     * @return the active Scene, or null before {@link #start} has been called
     */
    public static Scene getScene() {
        return scene;
    }

    public static void setRoot(String fxml) throws IOException {
        // Cleanup previous controller if it implements Cleanable
        cleanupCurrentController();

        FXMLLoader loader = new FXMLLoader(App.class.getResource(fxml + ".fxml"));
        Parent root = loader.load();
        currentController = loader.getController();
        scene.setRoot(root);
    }

    /**
     * Cleans up the current controller if it implements Cleanable.
     */
    private static void cleanupCurrentController() {
        if (currentController instanceof Cleanable) {
            System.out.println("Cleaning up controller: " + currentController.getClass().getSimpleName());
            ((Cleanable) currentController).cleanup();
        }
        currentController = null;
    }

    private static Parent loadFXML(String fxml) throws IOException {
        FXMLLoader fxmlLoader = new FXMLLoader(App.class.getResource(fxml + ".fxml"));
        Parent root = fxmlLoader.load();
        currentController = fxmlLoader.getController();
        return root;
    }

    /**
     * Main method to launch the JavaFX application and start the client controller in a separate thread.
     * With this setup, the client controller can handle server communication while the JavaFX UI runs in the main thread.
     * This allows the client to run concurrently with the JavaFX UI.
     *
     * @param args command line arguments
     */
    public static void main(String[] args) {
        Thread backGroundBackend = new Thread(() -> {
            try {
                ClientFactory.getClientController();
            } catch (RuntimeException e) {
                e.printStackTrace();
            }
        });
        backGroundBackend.setDaemon(true);
        backGroundBackend.start();
        launch();
    }

}