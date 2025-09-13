package org.example.Client;

import org.example.jsonOperator.service.JSONOperatorServiceStub;
import java.io.IOException;
import java.net.Socket;

public class ClientFactory {
    private static IClientController instance;

    public static synchronized IClientController getClientController() {
        if (instance == null) {
            try {
                Socket socket = new Socket("127.0.0.1", 55556);
                JSONOperatorServiceStub handler = new JSONOperatorServiceStub();

                ClientController controller = new ClientController(socket, handler);

                // Inject the controller into the handler
                handler.setClientController(controller);
                handler.initialize();
                controller.connectToServer();
                instance = controller;
            } catch (IOException e) {
                e.printStackTrace();
                throw new RuntimeException("Failed to initialize ClientController", e);
            }
        }
        return instance;
    }
}