package org.example.Client;

import com.fasterxml.jackson.databind.ObjectMapper;
import org.example.jsonOperator.service.JSONOperatorServiceStub;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.mockito.Mock;
import org.mockito.MockitoAnnotations;

import java.net.http.HttpClient;
import java.util.concurrent.TimeUnit;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.Mockito.*;

/**
 * Unit tests for RestClientController.
 */
class RestClientControllerTest {

    @Mock
    private JSONOperatorServiceStub jsonMessageHandler;

    private RestClientController restClientController;
    private AutoCloseable mocks;
    private static final String TEST_BASE_URL = "http://127.0.0.1:5000";

    @BeforeEach
    void setUp() {
        mocks = MockitoAnnotations.openMocks(this);
        restClientController = new RestClientController(TEST_BASE_URL, jsonMessageHandler);
    }

    @AfterEach
    void tearDown() throws Exception {
        if (restClientController != null) {
            restClientController.close();
        }
        if (mocks != null) {
            mocks.close();
        }
    }

    @Test
    void testConstructor() {
        assertNotNull(restClientController);
        assertFalse(restClientController.isConnected());
    }

    @Test
    void testSetJsonMessageHandler() {
        JSONOperatorServiceStub newHandler = mock(JSONOperatorServiceStub.class);
        restClientController.setJsonMessageHandler(newHandler);
        // No exception should be thrown
    }

    @Test
    void testIsConnectedInitially() {
        assertFalse(restClientController.isConnected());
    }

    @Test
    void testClose() {
        restClientController.close();
        assertFalse(restClientController.isConnected());
    }

    @Test
    void testSendMessage() {
        // sendMessage should not throw exception even though it's not actively used in REST
        assertDoesNotThrow(() -> restClientController.sendMessage("test message"));
    }

    @Test
    void testMultipleClosesCalls() {
        assertDoesNotThrow(() -> {
            restClientController.close();
            restClientController.close();
        });
    }

    @Test
    void testConstructorWithNullHandler() {
        // RestClientController stores the null handler without throwing
        // It will fail later when trying to use it
        assertDoesNotThrow(() -> {
            new RestClientController(TEST_BASE_URL, null);
        });
    }

    @Test
    void testConstructorWithNullBaseUrl() {
        // RestClientController stores the null URL without throwing
        // It will fail later when trying to connect
        assertDoesNotThrow(() -> {
            new RestClientController(null, jsonMessageHandler);
        });
    }

    // Note: Integration tests that actually connect to the server are in RestClientIntegrationTest
}
