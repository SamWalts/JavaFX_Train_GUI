package org.example.config;

import java.io.IOException;
import java.io.InputStream;
import java.util.Properties;
import java.util.logging.Logger;

/**
 * Singleton service for managing application configuration from properties file.
 * Thread-safe configuration access for REST and socket server settings.
 */
public class ConfigService {
    private static final Logger logger = Logger.getLogger(ConfigService.class.getName());
    private static ConfigService instance;
    private final Properties properties;

    private ConfigService() {
        properties = new Properties();
        loadProperties();
    }

    /**
     * Get singleton instance of ConfigService.
     *
     * @return ConfigService instance
     */
    public static synchronized ConfigService getInstance() {
        if (instance == null) {
            instance = new ConfigService();
        }
        return instance;
    }

    /**
     * Load properties from application.properties file.
     */
    private void loadProperties() {
        try (InputStream input = getClass().getResourceAsStream("/config/application.properties")) {
            if (input == null) {
                logger.warning("Unable to find application.properties, using defaults");
                setDefaults();
                return;
            }
            properties.load(input);
            logger.info("Configuration loaded successfully");
        } catch (IOException e) {
            logger.severe("Failed to load properties: " + e.getMessage());
            setDefaults();
        }
    }

    /**
     * Set default configuration values.
     */
    private void setDefaults() {
        properties.setProperty("rest.server.host", "127.0.0.1");
        properties.setProperty("rest.server.port", "5000");
        properties.setProperty("socket.server.host", "127.0.0.1");
        properties.setProperty("socket.server.port", "55556");
        properties.setProperty("polling.interval.seconds", "1");
    }

    /**
     * Get property value by key.
     *
     * @param key Property key
     * @return Property value or null if not found
     */
    public String getProperty(String key) {
        return properties.getProperty(key);
    }

    /**
     * Get property value with default fallback.
     *
     * @param key Property key
     * @param defaultValue Default value if key not found
     * @return Property value or default
     */
    public String getProperty(String key, String defaultValue) {
        return properties.getProperty(key, defaultValue);
    }

    /**
     * Get REST server base URL.
     *
     * @return Formatted base URL (e.g., "http://127.0.0.1:5000")
     */
    public String getRestServerBaseUrl() {
        String host = getProperty("rest.server.host", "127.0.0.1");
        String port = getProperty("rest.server.port", "5000");
        return String.format("http://%s:%s", host, port);
    }

    /**
     * Get socket server host.
     *
     * @return Socket server host
     */
    public String getSocketServerHost() {
        return getProperty("socket.server.host", "127.0.0.1");
    }

    /**
     * Get socket server port.
     *
     * @return Socket server port
     */
    public int getSocketServerPort() {
        String port = getProperty("socket.server.port", "55556");
        return Integer.parseInt(port);
    }

    /**
     * Get polling interval in seconds.
     *
     * @return Polling interval
     */
    public int getPollingIntervalSeconds() {
        String interval = getProperty("polling.interval.seconds", "1");
        return Integer.parseInt(interval);
    }
}
