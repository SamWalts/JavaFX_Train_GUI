package org.example.Client;

import org.example.jsonOperator.service.JSONOperatorServiceStub;

import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.net.Socket;

public interface IClientController {
    void sendMessage(String message);
    void connectToServer();
    void setJsonMessageHandler(JSONOperatorServiceStub handler);
    void startPollingServer();
    
    /**
     * Close everything (for socket-based implementations).
     * REST-based implementations may provide an empty implementation.
     */
    default void closeEverything(Socket socket, BufferedWriter bufferedWriter, BufferedReader bufferedReader) {
        // Default empty implementation for REST clients
    }
}