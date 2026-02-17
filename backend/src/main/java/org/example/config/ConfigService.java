package org.example.config;

import java.io.IOException;
import java.io.InputStream;
import java.util.Properties;
import java.util.logging.Logger;

/**
 * Singleton service for managing application configuration from properties file.
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
        try (InputStream input = getClass().getResourceAsStream("/application.properties")) {
            if (input == null) {
                logger.warning("Unable to find application.properties");
                return;
            }
            properties.load(input);
            logger.info("Configuration loaded successfully");
        } catch (IOException e) {
            logger.severe("Failed to load properties: " + e.getMessage());
        }
    }

    /**
     * Get property value by key.
     */
    public String getProperty(String key) {
        return properties.getProperty(key);
    }
}
