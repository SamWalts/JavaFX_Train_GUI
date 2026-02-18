package org.viewScreens;

import javafx.application.Platform;
import javafx.fxml.FXML;
import javafx.scene.control.Button;
import javafx.scene.image.ImageView;
import javafx.scene.layout.BorderPane;
import org.services.NavigationService;
import org.services.ResponsiveHelper;

/**
 * Controller for the Tram screen.
 *
 * <p>Currently a placeholder with responsive image binding and
 * navigation buttons. To extend:</p>
 * <ol>
 *   <li>Add new FXML controls to {@code tramScreen.fxml}.</li>
 *   <li>Declare matching {@code @FXML} fields here.</li>
 *   <li>Wire them in {@link #initialize()}.</li>
 * </ol>
 */
public class TramController {

    @FXML private BorderPane rootPane;
    @FXML private ImageView tramImage;
    @FXML private Button backToTrainButton;
    @FXML private Button utilitiesButton;

    @FXML
    public void initialize() {
        if (backToTrainButton != null) {
            backToTrainButton.setOnAction(e ->
                    NavigationService.getInstance().navigateWhenServerReady("trainScreen"));
        }
        if (utilitiesButton != null) {
            utilitiesButton.setOnAction(e ->
                    NavigationService.getInstance().navigateWhenServerReady("utilitiesScreen"));
        }
        Platform.runLater(this::bindResponsiveImage);
    }

    private void bindResponsiveImage() {
        if (tramImage == null) return;
        javafx.scene.Scene scene = tramImage.getScene();
        if (scene != null) {
            ResponsiveHelper.bindImageViewToScene(tramImage, scene, 0.80, 0.55);
        } else {
            tramImage.sceneProperty().addListener((obs, oldScene, newScene) -> {
                if (newScene != null) {
                    ResponsiveHelper.bindImageViewToScene(tramImage, newScene, 0.80, 0.55);
                }
            });
        }
    }
}
