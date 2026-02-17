package org.services;

import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.*;

/**
 * Unit tests for {@link ResponsiveHelper}.
 *
 * <p>These tests validate the pure-logic methods without requiring a
 * running JavaFX toolkit (Scene-dependent methods are tested via
 * parameterised calculations where possible).</p>
 */
class ResponsiveHelperTest {

    // ── computeScaleFactor ────────────────────────────────────────

    @Test
    void testComputeScaleFactor_nullScene_returnsOne() {
        double factor = ResponsiveHelper.computeScaleFactor(null, 1920, 1080);
        assertEquals(1.0, factor, "Null scene should return 1.0");
    }

    @Test
    void testComputeScaleFactor_invalidDesignWidth_throws() {
        assertThrows(IllegalArgumentException.class,
                () -> ResponsiveHelper.computeScaleFactor(null, 0, 1080),
                "Zero design width should throw");
    }

    @Test
    void testComputeScaleFactor_invalidDesignHeight_throws() {
        assertThrows(IllegalArgumentException.class,
                () -> ResponsiveHelper.computeScaleFactor(null, 1920, -1),
                "Negative design height should throw");
    }

    // ── scaleFactorBinding ────────────────────────────────────────

    @Test
    void testScaleFactorBinding_invalidDesign_throws() {
        assertThrows(IllegalArgumentException.class,
                () -> ResponsiveHelper.scaleFactorBinding(null, 0, 1080),
                "Zero design width should throw");
    }

    // ── scaledFontSize ────────────────────────────────────────────

    @Test
    void testScaledFontSize_atDesignScale() {
        double result = ResponsiveHelper.scaledFontSize(24.0, 1.0);
        assertEquals(24.0, result, 0.001);
    }

    @Test
    void testScaledFontSize_halfScale() {
        double result = ResponsiveHelper.scaledFontSize(24.0, 0.5);
        assertEquals(12.0, result, 0.001);
    }

    @Test
    void testScaledFontSize_neverBelowMinimum() {
        double result = ResponsiveHelper.scaledFontSize(10.0, 0.1);
        assertTrue(result >= 8.0, "Font size should never drop below 8.0");
    }

    @Test
    void testScaledFontSize_doubleScale() {
        double result = ResponsiveHelper.scaledFontSize(16.0, 2.0);
        assertEquals(32.0, result, 0.001);
    }

    @Test
    void testScaledFontSize_zeroScale_returnMinimum() {
        double result = ResponsiveHelper.scaledFontSize(20.0, 0.0);
        assertEquals(8.0, result, 0.001, "Zero scale should return minimum font size");
    }

    // ── bindImageViewToScene ──────────────────────────────────────

    @Test
    void testBindImageViewToScene_nullArgs_doesNotThrow() {
        assertDoesNotThrow(() -> ResponsiveHelper.bindImageViewToScene(null, null, 0.9, 0.7));
    }

    // ── applyContentScaling ───────────────────────────────────────

    @Test
    void testApplyContentScaling_nullArgs_doesNotThrow() {
        assertDoesNotThrow(() -> ResponsiveHelper.applyContentScaling(null, null, 1920, 1080));
    }

    // ── bindRegionToScene ─────────────────────────────────────────

    @Test
    void testBindRegionToScene_nullArgs_doesNotThrow() {
        assertDoesNotThrow(() -> ResponsiveHelper.bindRegionToScene(null, null));
    }

    // ── constants ─────────────────────────────────────────────────

    @Test
    void testDesignConstants() {
        assertEquals(1920.0, ResponsiveHelper.DESIGN_WIDTH);
        assertEquals(1080.0, ResponsiveHelper.DESIGN_HEIGHT);
    }
}
