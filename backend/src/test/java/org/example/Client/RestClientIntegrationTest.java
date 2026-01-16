package org.example.Client;

import org.example.jsonOperator.dao.HMIJSONDAOStub;
import org.example.jsonOperator.service.JSONOperatorServiceStub;
import org.junit.jupiter.api.*;

import java.util.concurrent.TimeUnit;

import static org.junit.jupiter.api.Assertions.*;

/**
 * Integration tests for RestClientController.
 * These tests require the Python REST server to be running.
 */
@TestMethodOrder(MethodOrderer.OrderAnnotation.class)
class RestClientIntegrationTest {

    private static final String BASE_URL = "http://127.0.0.1:5000";
    private RestClientController restClientController;
    private JSONOperatorServiceStub jsonOperatorService;
    private HMIJSONDAOStub daoStub;

    @BeforeEach
    void setUp() {
        daoStub = new HMIJSONDAOStub();
        jsonOperatorService = new JSONOperatorServiceStub();
        restClientController = new RestClientController(BASE_URL, jsonOperatorService);
    }

    @AfterEach
    void tearDown() {
        if (restClientController != null) {
            restClientController.close();
        }
    }

    @Test
    @Order(1)
    void testConnectToServer() throws InterruptedException {
        restClientController.connectToServer();
        
        // Wait for connection to establish
        TimeUnit.SECONDS.sleep(2);
        
        assertTrue(restClientController.isConnected());
    }

    @Test
    @Order(2)
    void testReceiveInitialData() throws InterruptedException {
        restClientController.connectToServer();
        
        // Wait for initial data fetch
        TimeUnit.SECONDS.sleep(2);
        
        // Verify connection was established
        assertTrue(restClientController.isConnected());
    }

    @Test
    @Order(3)
    void testPollingWorksWithoutErrors() throws InterruptedException {
        restClientController.connectToServer();
        
        // Wait for connection
        TimeUnit.SECONDS.sleep(2);
        
        // Let polling run for a bit
        TimeUnit.SECONDS.sleep(3);
        
        // Should still be connected
        assertTrue(restClientController.isConnected());
    }

    @Test
    @Order(4)
    void testCloseWhileConnected() throws InterruptedException {
        restClientController.connectToServer();
        TimeUnit.SECONDS.sleep(1);
        
        // Close should work without errors
        assertDoesNotThrow(() -> restClientController.close());
        assertFalse(restClientController.isConnected());
    }

    @Test
    @Order(5)
    void testMultipleCloseCalls() {
        restClientController.connectToServer();
        
        // Multiple closes should not cause errors
        assertDoesNotThrow(() -> {
            restClientController.close();
            restClientController.close();
        });
    }
}
