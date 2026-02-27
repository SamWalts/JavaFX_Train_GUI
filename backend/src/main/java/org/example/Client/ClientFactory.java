package org.example.Client;

import org.example.config.ConfigService;
import org.example.jsonOperator.service.JSONOperatorServiceStub;
import java.io.IOException;
import java.net.Socket;
import java.util.logging.Logger;

public class ClientFactory {
    private static final Logger logger = Logger.getLogger(ClientFactory.class.getName());
    private static IClientController instance;


    public static synchronized IClientController getClientController() {
        if (instance == null) {
            logger.info("Attempting to connect to Rest server.");
            JSONOperatorServiceStub handler = new JSONOperatorServiceStub();

            RestClientController controller = new RestClientController(handler);

            // Inject the controller into the handler
            handler.setClientController(controller);
            handler.initialize();
            controller.connectToServer();
            instance = controller;
            logger.info("ClientController initialized and connected successfully.");
        }
        return instance;
    }

    /**
     * Shuts down the client controller and releases all resources.
     * Call this when the application is exiting.
     */
    public static synchronized void shutdown() {
        if (instance != null) {
            logger.info("Shutting down ClientController...");
            if (instance instanceof RestClientController restController) {
                restController.close();
            }
            instance = null;
            logger.info("ClientController shutdown complete.");
        }
    }
}

