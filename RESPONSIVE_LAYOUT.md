# Responsive / Dynamic Layout Guide

This document explains how the JavaFX Train GUI adapts to any screen size
and how to extend the system when adding new screens or controls.

## Table of Contents

1. [Overview](#overview)
2. [Key Components](#key-components)
3. [How It Works](#how-it-works)
4. [Adding a New Responsive Screen](#adding-a-new-responsive-screen)
5. [Adding Responsive Images](#adding-responsive-images)
6. [Scaling Absolute-Position Layouts](#scaling-absolute-position-layouts)
7. [CSS Stylesheet Guide](#css-stylesheet-guide)
8. [ResponsiveHelper API](#responsivehelper-api)
9. [Testing](#testing)

## Overview

The application window dynamically sizes itself to **80 % of the primary
display** on start-up. All screens use one of two strategies to stay
usable on any resolution:

| Strategy | Used by | How |
|----------|---------|-----|
| **Flow layouts** (`VBox`, `BorderPane`, `ScrollPane`) | Title, Tram, Utilities | Containers stretch/wrap naturally |
| **Uniform scaling** (`Scale` transform) | Train screen | The fixed-position `AnchorPane` is scaled as a single unit |

A shared CSS stylesheet (`styles.css`) provides consistent look-and-feel
across all screens.

## Key Components

| File | Role |
|------|------|
| `App.java` | Detects screen size, creates scene, loads global CSS |
| `ResponsiveHelper.java` | Static utility methods for scaling and binding |
| `styles.css` | Shared style classes (buttons, labels, overlays, …) |
| `title.fxml` | Responsive flow layout (ScrollPane → VBox) |
| `trainScreen.fxml` | Scalable absolute layout (ScrollPane → StackPane → AnchorPane) |
| `tramScreen.fxml` | Responsive flow layout (ScrollPane → BorderPane) |
| `utilitiesScreen.fxml` | Responsive flow layout (ScrollPane → BorderPane) |

## How It Works

### 1. Dynamic Window Size (`App.java`)

```java
Rectangle2D screenBounds = Screen.getPrimary().getVisualBounds();
double width  = screenBounds.getWidth()  * 0.80;
double height = screenBounds.getHeight() * 0.80;
scene = new Scene(loadFXML("title"), width, height);
```

The constant `SCREEN_USAGE_FRACTION` can be changed in one place.

### 2. Global Stylesheet

```java
scene.getStylesheets().add(
    App.class.getResource("styles.css").toExternalForm());
```

Every screen loaded via `App.setRoot()` inherits the same styles.

### 3. Responsive Images

Images are bound to a fraction of the scene dimensions so they grow or
shrink with the window:

```java
ResponsiveHelper.bindImageViewToScene(imageView, scene, 0.90, 0.55);
//                                                       ↑width  ↑height
```

### 4. Content Scaling (Train Screen)

The track diagram uses absolute (x, y) positions inside an `AnchorPane`
designed at 1920 × 1080. Rather than re-laying out every child, a
`Scale` transform is applied:

```java
ResponsiveHelper.applyContentScaling(
    trainContent, scene,
    ResponsiveHelper.DESIGN_WIDTH,   // 1920
    ResponsiveHelper.DESIGN_HEIGHT); // 1080
```

The scale factor equals `min(sceneWidth/1920, sceneHeight/1080)`,
preserving aspect ratio.

## Adding a New Responsive Screen

Follow these steps to add a screen that works on any display size.

### Step 1 – Create the FXML

Use a `ScrollPane` as root so content is always reachable:

```xml
<ScrollPane fitToWidth="true" fitToHeight="true" pannable="true"
            fx:controller="org.viewScreens.MyScreenController"
            styleClass="my-screen">
    <content>
        <BorderPane fx:id="rootPane">
            <center>
                <VBox alignment="CENTER" spacing="20.0">
                    <!-- Add controls here -->
                    <ImageView fx:id="myImage" preserveRatio="true">
                        <image>
                            <Image url="@../../images/myImage.png" />
                        </image>
                    </ImageView>
                </VBox>
            </center>
            <bottom>
                <HBox alignment="CENTER" spacing="20.0">
                    <Button fx:id="backButton" text="Back" styleClass="nav-button" />
                </HBox>
            </bottom>
        </BorderPane>
    </content>
</ScrollPane>
```

### Step 2 – Create the Controller

```java
public class MyScreenController {

    @FXML private ImageView myImage;
    @FXML private Button backButton;

    @FXML
    public void initialize() {
        backButton.setOnAction(e ->
            NavigationService.getInstance().navigateWhenServerReady("trainScreen"));

        Platform.runLater(this::bindResponsiveImage);
    }

    private void bindResponsiveImage() {
        if (myImage == null) return;
        Scene scene = myImage.getScene();
        if (scene != null) {
            ResponsiveHelper.bindImageViewToScene(myImage, scene, 0.80, 0.55);
        } else {
            myImage.sceneProperty().addListener((obs, o, n) -> {
                if (n != null)
                    ResponsiveHelper.bindImageViewToScene(myImage, n, 0.80, 0.55);
            });
        }
    }
}
```

### Step 3 – Add Navigation

From an existing controller, navigate with:

```java
NavigationService.getInstance().navigateWhenServerReady("myScreen");
```

### Step 4 – Add Styles (Optional)

Add a class in `styles.css`:

```css
.my-screen {
    -fx-background-color: #1a1a2e;
}
```

## Adding Responsive Images

1. Place the image file in `frontend/src/main/resources/images/`.
2. Reference it in FXML:
   ```xml
   <ImageView fx:id="myImage" preserveRatio="true">
       <image><Image url="@../../images/myImage.png" /></image>
   </ImageView>
   ```
3. Bind in the controller:
   ```java
   ResponsiveHelper.bindImageViewToScene(myImage, scene, widthFraction, heightFraction);
   ```

If you need different image sizes for different screen densities, supply
multiple image files (e.g. `icon.png`, `icon@2x.png`) and select the
appropriate one based on `Screen.getPrimary().getOutputScaleX()`.

## Scaling Absolute-Position Layouts

When a layout *must* use absolute coordinates (e.g. the track diagram),
wrap it in a `StackPane` and apply `ResponsiveHelper.applyContentScaling`:

```xml
<ScrollPane fitToWidth="true" fitToHeight="true">
    <StackPane fx:id="scalingWrapper" alignment="TOP_LEFT">
        <AnchorPane fx:id="content" prefWidth="1920" prefHeight="1080">
            <!-- Children with layoutX / layoutY -->
        </AnchorPane>
    </StackPane>
</ScrollPane>
```

```java
ResponsiveHelper.applyContentScaling(content, scene, 1920, 1080);
```

## CSS Stylesheet Guide

The stylesheet `styles.css` is loaded once in `App.java` and applies to
every screen. Key classes:

| Class | Where used | Purpose |
|-------|-----------|---------|
| `.nav-button` | All screens | Navigation button styling with hover/press states |
| `.control-button` | Train screen | Orange action buttons (Horn, Whistle, Bell) |
| `.speed-label` | Train screen | White bold speed readout |
| `.switch-overlay` | Train screen | Invisible clickable overlay |
| `.switch-overlay-flash` | Train screen | Green-border flash during ACK wait |
| `.data-grid` | Title screen | Grid spacing for HMI data |
| `.title-text` | Title screen | Railroad title text styling |
| `.tram-placeholder-label` | Tram screen | Placeholder text |
| `.utilities-placeholder-label` | Utilities screen | Placeholder text |

To add a new style, append it to `styles.css` with a descriptive comment.

## ResponsiveHelper API

All methods are `static` and documented with Javadoc.

| Method | Description |
|--------|-------------|
| `computeScaleFactor(scene, dw, dh)` | Returns `min(sw/dw, sh/dh)` |
| `scaleFactorBinding(scene, dw, dh)` | Live `DoubleBinding` of the scale factor |
| `bindImageViewToScene(iv, scene, wf, hf)` | Binds image fit-width/height to scene fractions |
| `applyContentScaling(node, scene, dw, dh)` | Adds a `Scale` transform driven by scene size |
| `bindRegionToScene(region, scene)` | Binds region pref size to full scene size |
| `scaledFontSize(base, scale)` | Returns scaled font size (min 8 px) |

Constants: `DESIGN_WIDTH = 1920`, `DESIGN_HEIGHT = 1080`.

## Testing

### Unit Tests

`ResponsiveHelperTest.java` validates pure-logic methods (scale
computation, font scaling, null safety). Run with:

```bash
mvn test -Dtest=ResponsiveHelperTest -pl frontend
```

### Manual Verification

1. Build and run:
   ```bash
   mvn clean install -DskipTests
   cd frontend && mvn javafx:run
   ```
2. Resize the window – the title image and train diagram should scale.
3. Try fullscreen – content should fill the window proportionally.
4. Navigate between screens – styles should be consistent.
