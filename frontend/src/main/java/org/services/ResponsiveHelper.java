package org.services;

import javafx.beans.binding.DoubleBinding;
import javafx.beans.property.ReadOnlyDoubleProperty;
import javafx.scene.Node;
import javafx.scene.Scene;
import javafx.scene.image.ImageView;
import javafx.scene.layout.Region;
import javafx.scene.transform.Scale;

/**
 * Utility class providing responsive/dynamic layout helpers for JavaFX screens.
 *
 * <h2>Overview</h2>
 * This helper enables the JavaFX Train GUI to adapt to any screen size by
 * providing methods that compute scale factors, bind image sizes, and apply
 * content scaling relative to a design-time reference resolution.
 *
 * <h2>Usage</h2>
 * <pre>{@code
 * // In a controller's initialize() method:
 * Scene scene = myNode.getScene();
 * double scaleFactor = ResponsiveHelper.computeScaleFactor(scene, 1920, 1080);
 *
 * // Bind an ImageView to fill a percentage of the scene width:
 * ResponsiveHelper.bindImageViewToScene(imageView, scene, 0.9, 0.7);
 *
 * // Apply uniform scaling to an entire content pane:
 * ResponsiveHelper.applyContentScaling(contentPane, scene, 1920, 1080);
 * }</pre>
 *
 * <h2>Extending</h2>
 * To add new responsive behaviors:
 * <ol>
 *   <li>Add a new static method to this class following the existing patterns.</li>
 *   <li>Document the design-time reference values the method expects.</li>
 *   <li>Add corresponding unit tests in {@code ResponsiveHelperTest}.</li>
 * </ol>
 */
public final class ResponsiveHelper {

    /** Default design-time width used throughout the application (px). */
    public static final double DESIGN_WIDTH = 1920.0;

    /** Default design-time height used throughout the application (px). */
    public static final double DESIGN_HEIGHT = 1080.0;

    private ResponsiveHelper() {
        // utility class – not instantiable
    }

    /**
     * Computes a uniform scale factor so that content designed for
     * {@code designWidth × designHeight} fits within the current scene,
     * preserving aspect ratio.
     *
     * @param scene       the current scene (must not be null)
     * @param designWidth  the width the content was designed for
     * @param designHeight the height the content was designed for
     * @return scale factor (≤ 1.0 when smaller than design, ≥ 1.0 when larger)
     * @throws IllegalArgumentException if designWidth or designHeight ≤ 0
     */
    public static double computeScaleFactor(Scene scene, double designWidth, double designHeight) {
        if (designWidth <= 0 || designHeight <= 0) {
            throw new IllegalArgumentException("Design dimensions must be positive");
        }
        if (scene == null) {
            return 1.0;
        }
        double scaleX = scene.getWidth() / designWidth;
        double scaleY = scene.getHeight() / designHeight;
        return Math.min(scaleX, scaleY);
    }

    /**
     * Creates a {@link DoubleBinding} that always reflects the current uniform
     * scale factor for the given scene, reacting to width/height changes.
     *
     * @param scene        the scene to observe
     * @param designWidth  reference design width
     * @param designHeight reference design height
     * @return a live DoubleBinding of the scale factor
     */
    public static DoubleBinding scaleFactorBinding(Scene scene, double designWidth, double designHeight) {
        if (designWidth <= 0 || designHeight <= 0) {
            throw new IllegalArgumentException("Design dimensions must be positive");
        }
        ReadOnlyDoubleProperty w = scene.widthProperty();
        ReadOnlyDoubleProperty h = scene.heightProperty();
        return new DoubleBinding() {
            { super.bind(w, h); }

            @Override
            protected double computeValue() {
                double sx = w.get() / designWidth;
                double sy = h.get() / designHeight;
                return Math.min(sx, sy);
            }
        };
    }

    /**
     * Binds an {@link ImageView}'s fit-width and fit-height to percentages
     * of the scene dimensions, so the image scales with the window.
     *
     * @param imageView     the image view to bind
     * @param scene         the scene whose size drives the binding
     * @param widthFraction  fraction of scene width (0.0–1.0)
     * @param heightFraction fraction of scene height (0.0–1.0)
     */
    public static void bindImageViewToScene(ImageView imageView, Scene scene,
                                            double widthFraction, double heightFraction) {
        if (imageView == null || scene == null) return;
        imageView.setPreserveRatio(true);
        imageView.fitWidthProperty().bind(scene.widthProperty().multiply(widthFraction));
        imageView.fitHeightProperty().bind(scene.heightProperty().multiply(heightFraction));
    }

    /**
     * Applies a live {@link Scale} transform to a content node so that it
     * scales uniformly to fit the scene, based on a design-time reference size.
     * The scale pivots from the top-left corner.
     *
     * <p>This is especially useful for screens using absolute positioning
     * (e.g., {@code AnchorPane} with fixed layoutX/layoutY) that need to scale
     * as a unit without re-laying-out every child.</p>
     *
     * @param content      the node (typically the root or a wrapper) to scale
     * @param scene        the scene whose size drives the scaling
     * @param designWidth  the width the layout was designed at
     * @param designHeight the height the layout was designed at
     */
    public static void applyContentScaling(Node content, Scene scene,
                                           double designWidth, double designHeight) {
        if (content == null || scene == null) return;
        DoubleBinding factor = scaleFactorBinding(scene, designWidth, designHeight);
        Scale scale = new Scale();
        scale.xProperty().bind(factor);
        scale.yProperty().bind(factor);
        scale.setPivotX(0);
        scale.setPivotY(0);
        content.getTransforms().add(scale);
    }

    /**
     * Binds the min/pref/max size of a {@link Region} to the full scene
     * dimensions, so it always fills the window.
     *
     * @param region the region to bind
     * @param scene  the scene providing size
     */
    public static void bindRegionToScene(Region region, Scene scene) {
        if (region == null || scene == null) return;
        region.prefWidthProperty().bind(scene.widthProperty());
        region.prefHeightProperty().bind(scene.heightProperty());
    }

    /**
     * Computes a scaled font size relative to the design-time resolution.
     *
     * @param baseFontSize   font size at design-time resolution
     * @param currentScale   current scale factor (from {@link #computeScaleFactor})
     * @return the scaled font size (never below {@code MIN_FONT})
     */
    public static double scaledFontSize(double baseFontSize, double currentScale) {
        double MIN_FONT = 8.0;
        return Math.max(MIN_FONT, baseFontSize * currentScale);
    }
}
