package org.example.Client;

import org.example.jsonOperator.service.JSONOperatorServiceStub;
import java.io.IOException;
import java.net.Socket;
import java.util.logging.Logger;

public class ClientFactory {
    private static final Logger logger = Logger.getLogger(ClientFactory.class.getName());
    private static IClientController instance;

    public static synchronized IClientController getClientController() {
        if (instance == null) {
            try {
                logger.info("Attempting to connect to server at 127.0.0.1:55556");
                Socket socket = new Socket("127.0.0.1", 55556);
                JSONOperatorServiceStub handler = new JSONOperatorServiceStub();

                ClientController controller = new ClientController(socket, handler);

                // Inject the controller into the handler
                handler.setClientController(controller);
                handler.initialize();
                controller.connectToServer();
                instance = controller;
                logger.info("ClientController initialized and connected successfully.");
            } catch (IOException e) {
                logger.severe("Failed to initialize ClientController: " + e.getMessage());
                throw new RuntimeException("Failed to initialize ClientController", e);
            }
        }
        return instance;
    }
}