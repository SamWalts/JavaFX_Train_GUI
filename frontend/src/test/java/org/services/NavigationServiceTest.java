package org.services;

import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

import java.util.Set;

import static org.junit.jupiter.api.Assertions.*;

class NavigationServiceTest {

    private NavigationService navigationService;
    private UIStateService uiStateService;

    @BeforeEach
    void setUp() {
        navigationService = NavigationService.getInstance();
        uiStateService = UIStateService.getInstance();
        // Clear any state from previous tests
        uiStateService.clearAllPending();
    }

    @AfterEach
    void tearDown() {
        // Clean up after each test
        uiStateService.clearAllPending();
    }

    @Test
    void testSingletonInstance() {
        // Get two instances
        NavigationService instance1 = NavigationService.getInstance();
        NavigationService instance2 = NavigationService.getInstance();

        // Verify they are the same instance
        assertSame(instance1, instance2, "NavigationService should be a singleton");
    }

    @Test
    void testNavigateWhenServerReadyWithNullTargetId() {
        // Should not throw an exception
        assertDoesNotThrow(() -> navigationService.navigateWhenServerReady(null),
                "Should handle null targetId gracefully");
    }

    @Test
    void testNavigateWhenServerReadyWithEmptyTargetId() {
        // Should not throw an exception
        assertDoesNotThrow(() -> navigationService.navigateWhenServerReady(""),
                "Should handle empty targetId gracefully");
    }

    @Test
    void testNavigateNowWithNullTargetId() {
        // Should not throw an exception
        assertDoesNotThrow(() -> navigationService.navigateNow(null),
                "Should handle null targetId gracefully");
    }

    @Test
    void testNavigateNowWithEmptyTargetId() {
        // Should not throw an exception
        assertDoesNotThrow(() -> navigationService.navigateNow(""),
                "Should handle empty targetId gracefully");
    }

    @Test
    void testNavigationServiceDeferredNavigationLogic() {
        // Verify that NavigationService defers navigation when UIStateService is waiting
        // This test only validates the deferral logic without triggering actual navigation
        
        // Mark as waiting BEFORE attempting navigation
        uiStateService.markPending(Set.of("key1"));
        assertTrue(uiStateService.isWaitingForServer(), "UIState should be waiting for server");
        
        // NavigationService should defer navigation when server is waiting
        // Since we're waiting, this should NOT call navigateNow immediately
        // Instead it should register a listener and store the pending target
        assertDoesNotThrow(() -> navigationService.navigateWhenServerReady("someView"),
                "NavigationService should defer navigation without error");
        
        // The navigation should still be pending (deferred)
        assertTrue(uiStateService.isWaitingForServer(), "Should still be waiting after deferred navigation");
    }

    /**
     * Note: Full integration tests for NavigationService would require:
     * 1. Initializing the JavaFX toolkit (Platform.startup())
     * 2. Mocking or stubbing the App.setRoot() method
     * 3. Using TestFX or similar framework for JavaFX testing
     * 
     * These tests verify the basic logic and integration with UIStateService
     * without requiring full JavaFX initialization. For complete coverage,
     * consider adding UI tests using TestFX in a separate test suite.
     */
}
