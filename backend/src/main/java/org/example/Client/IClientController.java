package org.example.Client;

import org.example.jsonOperator.service.JSONOperatorServiceStub;

import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.net.Socket;

public interface IClientController {
    void sendMessage(String message);
    void connectToServer();
    void setJsonMessageHandler(JSONOperatorServiceStub handler);
    void closeEverything(Socket socket, BufferedWriter bufferedWriter, BufferedReader bufferedReader);
}