package org.viewScreens;

import javafx.application.Platform;
import javafx.fxml.FXML;
import javafx.scene.control.Button;
import javafx.scene.image.ImageView;
import javafx.scene.layout.BorderPane;
import org.services.NavigationService;
import org.services.ResponsiveHelper;

/**
 * Controller for the Utilities screen.
 *
 * <p>Currently a placeholder with responsive image binding and
 * navigation buttons. To extend:</p>
 * <ol>
 *   <li>Add new FXML controls to {@code utilitiesScreen.fxml}.</li>
 *   <li>Declare matching {@code @FXML} fields here.</li>
 *   <li>Wire them in {@link #initialize()}.</li>
 * </ol>
 */
public class UtilitiesController {

    @FXML private BorderPane rootPane;
    @FXML private ImageView utilityImage;
    @FXML private Button backToTrainButton;
    @FXML private Button tramButton;

    @FXML
    public void initialize() {
        if (backToTrainButton != null) {
            backToTrainButton.setOnAction(e ->
                    NavigationService.getInstance().navigateWhenServerReady("trainScreen"));
        }
        if (tramButton != null) {
            tramButton.setOnAction(e ->
                    NavigationService.getInstance().navigateWhenServerReady("tramScreen"));
        }
        Platform.runLater(this::bindResponsiveImage);
    }

    private void bindResponsiveImage() {
        if (utilityImage == null) return;
        javafx.scene.Scene scene = utilityImage.getScene();
        if (scene != null) {
            ResponsiveHelper.bindImageViewToScene(utilityImage, scene, 0.80, 0.55);
        } else {
            utilityImage.sceneProperty().addListener((obs, oldScene, newScene) -> {
                if (newScene != null) {
                    ResponsiveHelper.bindImageViewToScene(utilityImage, newScene, 0.80, 0.55);
                }
            });
        }
    }
}
