package org.example.Client;

import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.example.config.ConfigService;
import org.example.jsonOperator.service.JSONOperatorServiceStub;

import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.time.Duration;
import java.util.Map;
import java.util.concurrent.Executors;
import java.util.concurrent.ScheduledExecutorService;
import java.util.concurrent.TimeUnit;
import java.util.logging.Level;
import java.util.logging.Logger;

/**
 * REST-based client controller for communicating with the Python REST server.
 * Replaces socket-based ClientController with HTTP/REST communication.
 */
public class RestClientController implements IClientController {
    private static final Logger logger = Logger.getLogger(RestClientController.class.getName());
    
    private final String baseUrl;
    private final HttpClient httpClient;
    private final ObjectMapper objectMapper;
    private JSONOperatorServiceStub jsonMessageHandler;
    private final ScheduledExecutorService scheduler = Executors.newScheduledThreadPool(1);
    private boolean connected = false;
    
    /**
     * Constructor for RestClientController with explicit URL.
     *
     * @param baseUrl Base URL of the REST server (e.g., "http://127.0.0.1:5000")
     * @param jsonMessageHandler Handler for JSON messages
     */
    public RestClientController(String baseUrl, JSONOperatorServiceStub jsonMessageHandler) {
        this.baseUrl = baseUrl;
        this.jsonMessageHandler = jsonMessageHandler;
        this.objectMapper = new ObjectMapper();
        this.httpClient = HttpClient.newBuilder()
                .connectTimeout(Duration.ofSeconds(10))
                .build();

        logger.log(Level.INFO, "RestClientController created for URL: {0}", baseUrl);
    }

    /**
     * Constructor for RestClientController using ConfigService.
     *
     * @param jsonMessageHandler Handler for JSON messages
     */
    public RestClientController(JSONOperatorServiceStub jsonMessageHandler) {
        ConfigService config = ConfigService.getInstance();

        this.baseUrl = config.getProperty("serverUrl") + ":" + config.getProperty("serverPort");
        this.jsonMessageHandler = jsonMessageHandler;
        this.objectMapper = new ObjectMapper();
        this.httpClient = HttpClient.newBuilder()
                .connectTimeout(Duration.ofSeconds(10))
                .build();

        logger.log(Level.INFO, "RestClientController created for URL: {0}", baseUrl);
    }

    
    /**
     * Set the JSON message handler.
     * 
     * @param handler JSONOperatorServiceStub
     */
    public void setJsonMessageHandler(JSONOperatorServiceStub handler) {
        this.jsonMessageHandler = handler;
    }
    
    /**
     * Connect to the server and start polling.
     */
    @Override
    public void connectToServer() {
        try {
            // Check if server is healthy
            if (checkServerHealth()) {
                connected = true;
                logger.info("Successfully connected to REST server");
                
                // Get initial database state
                fetchInitialData();
                
                // Start polling for updates
                startPollingServer();
            } else {
                logger.warning("Server health check failed");
            }
        } catch (Exception e) {
            logger.log(Level.SEVERE, "Error connecting to server: {0}", e.getMessage());
        }
    }
    
    /**
     * Check server health.
     * 
     * @return true if server is healthy
     */
    private boolean checkServerHealth() {
        try {
            HttpRequest request = HttpRequest.newBuilder()
                    .uri(URI.create(baseUrl + "/health"))
                    .GET()
                    .build();
            
            HttpResponse<String> response = httpClient.send(request, HttpResponse.BodyHandlers.ofString());
            
            if (response.statusCode() == 200) {
                Map<String, Object> healthData = objectMapper.readValue(response.body(), 
                        new TypeReference<Map<String, Object>>() {});
                logger.log(Level.INFO, "Server health: {0}", healthData.get("status"));
                return "healthy".equals(healthData.get("status"));
            }
            return false;
        } catch (Exception e) {
            logger.log(Level.WARNING, "Health check failed: {0}", e.getMessage());
            return false;
        }
    }
    
    /**
     * Fetch initial database state from server.
     */
    private void fetchInitialData() {
        try {
            HttpRequest request = HttpRequest.newBuilder()
                    .uri(URI.create(baseUrl + "/api/hmi/get-all"))
                    .GET()
                    .build();
            
            HttpResponse<String> response = httpClient.send(request, HttpResponse.BodyHandlers.ofString());
            
            if (response.statusCode() == 200) {
                String jsonData = response.body();
                jsonMessageHandler.writeStringToMap(jsonData);
                logger.info("Fetched initial database state");
            } else {
                logger.log(Level.WARNING, "Failed to fetch initial data: {0}", response.statusCode());
            }
        } catch (Exception e) {
            logger.log(Level.SEVERE, "Error fetching initial data: {0}", e.getMessage());
        }
    }
    
    /**
     * Start polling the server for updates.
     */
    @Override
    public void startPollingServer() {
        scheduler.scheduleAtFixedRate(() -> {
            try {
                checkForUpdates();
                sendPendingUpdates();
            } catch (Exception e) {
                logger.log(Level.WARNING, "Error during poll: {0}", e.getMessage());
            }
        }, 1, 1, TimeUnit.SECONDS);
    }
    
    /**
     * Check for updates from the server.
     */
    private void checkForUpdates() {
        try {
            // Check if updates are available
            HttpRequest checkRequest = HttpRequest.newBuilder()
                    .uri(URI.create(baseUrl + "/api/hmi/check-updates"))
                    .GET()
                    .build();
            
            HttpResponse<String> checkResponse = httpClient.send(checkRequest, 
                    HttpResponse.BodyHandlers.ofString());
            
            if (checkResponse.statusCode() == 200) {
                Map<String, Object> checkData = objectMapper.readValue(checkResponse.body(), 
                        new TypeReference<Map<String, Object>>() {});
                
                Boolean hasUpdates = (Boolean) checkData.get("has_updates");
                if (Boolean.TRUE.equals(hasUpdates)) {
                    // Fetch the updates
                    fetchUpdates();
                }
            }
        } catch (Exception e) {
            logger.log(Level.WARNING, "Error checking for updates: {0}", e.getMessage());
        }
    }
    
    /**
     * Fetch updates from the server.
     */
    private void fetchUpdates() {
        try {
            HttpRequest request = HttpRequest.newBuilder()
                    .uri(URI.create(baseUrl + "/api/hmi/get-updates"))
                    .GET()
                    .build();
            
            HttpResponse<String> response = httpClient.send(request, HttpResponse.BodyHandlers.ofString());
            
            if (response.statusCode() == 200) {
                String jsonData = response.body();
                if (jsonData != null && !jsonData.equals("[]")) {
                    jsonMessageHandler.writeStringToMap(jsonData);
                    jsonMessageHandler.finalizeSentData();
                    logger.info("Received and processed updates from server");
                }
            }
        } catch (Exception e) {
            logger.log(Level.SEVERE, "Error fetching updates: {0}", e.getMessage());
        }
    }
    
    /**
     * Send pending updates to the server.
     */
    private void sendPendingUpdates() {
        try {
            boolean hasUpdates = jsonMessageHandler.hasUpdatedHMI_READi();
            logger.log(Level.FINE, "Checking for pending updates. hasUpdatedHMI_READi={0}", hasUpdates);

            if (hasUpdates) {
                String payload = jsonMessageHandler.prepareDataForSending();
                logger.log(Level.INFO, "Prepared payload for sending: {0}", payload);

                if (payload != null && !payload.equals("[]")) {
                    logger.log(Level.INFO, "Sending POST to {0}/api/hmi/send-updates", baseUrl);
                    HttpRequest request = HttpRequest.newBuilder()
                            .uri(URI.create(baseUrl + "/api/hmi/send-updates"))
                            .header("Content-Type", "application/json")
                            .POST(HttpRequest.BodyPublishers.ofString(payload))
                            .build();
                    
                    HttpResponse<String> response = httpClient.send(request, 
                            HttpResponse.BodyHandlers.ofString());
                    
                    logger.log(Level.INFO, "Server response: status={0}, body={1}",
                            new Object[]{response.statusCode(), response.body()});

                    if (response.statusCode() == 200) {
                        Map<String, Object> responseData = objectMapper.readValue(response.body(), 
                                new TypeReference<Map<String, Object>>() {});
                        Boolean success = (Boolean) responseData.get("success");
                        if (Boolean.TRUE.equals(success)) {
                            jsonMessageHandler.finalizeSentData();
                            logger.info("Successfully sent updates to server");
                        }
                    } else {
                        logger.log(Level.WARNING, "Failed to send updates: {0}", response.statusCode());
                    }
                } else {
                    logger.log(Level.FINE, "Payload was empty, skipping send");
                }
            }
        } catch (Exception e) {
            logger.log(Level.WARNING, "Error sending updates: {0}", e.getMessage());
            e.printStackTrace();
        }
    }
    
    /**
     * Send a message to the server (for compatibility with IClientController interface).
     * Not directly used in REST implementation.
     * 
     * @param message Message to send
     */
    @Override
    public void sendMessage(String message) {
        // This method is kept for interface compatibility but is not used in REST implementation
        logger.log(Level.FINE, "sendMessage called (REST implementation uses HTTP methods): {0}", message);
    }
    
    /**
     * Check if the client is connected.
     * 
     * @return true if connected
     */
    public boolean isConnected() {
        return connected;
    }
    
    /**
     * Close the client connection.
     */
    public void close() {
        scheduler.shutdown();
        try {
            if (!scheduler.awaitTermination(5, TimeUnit.SECONDS)) {
                scheduler.shutdownNow();
            }
        } catch (InterruptedException e) {
            scheduler.shutdownNow();
            Thread.currentThread().interrupt();
        }
        connected = false;
        logger.info("RestClientController closed");
    }
}
