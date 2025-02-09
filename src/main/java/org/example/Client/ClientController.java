package org.example.Client;

import java.io.*;
import java.net.Socket;
import java.nio.charset.StandardCharsets;
import java.util.concurrent.BlockingQueue;
import java.util.concurrent.LinkedBlockingQueue;

import org.example.jsonOperator.dao.ListenerConcurrentMap;
import org.example.jsonOperator.dto.HmiData;
import org.example.jsonOperator.service.JSONOperatorServiceStub;

public class ClientController {

    private Socket socket;
    BufferedReader bufferedReader;
    private InputStreamReader inputStreamReader;
    BufferedWriter bufferedWriter;
    private JSONOperatorServiceStub jsonMessageHandler;
    private BlockingQueue<String> messageQueue;

    private final String nickname = "HMI";

    public ClientController(Socket socket) {
        try {
            this.socket = socket;
            this.bufferedReader = new BufferedReader(new InputStreamReader(socket.getInputStream(), StandardCharsets.UTF_8));
            this.inputStreamReader = new InputStreamReader(socket.getInputStream(), StandardCharsets.UTF_8);
            this.bufferedWriter = new BufferedWriter(new OutputStreamWriter(socket.getOutputStream(), StandardCharsets.UTF_8));
            this.jsonMessageHandler = new JSONOperatorServiceStub();
            this.messageQueue = new LinkedBlockingQueue<>();
            processMessages();
        } catch (IOException e) {
            closeEverything(socket, bufferedWriter, bufferedReader);
        }
    }

    public void sendMessage(String message) {
        System.out.println("Client: " + message);
        try {
            if (socket.isConnected()) {
                bufferedWriter.write(message);
                bufferedWriter.flush();
            }
        } catch (IOException e) {
            closeEverything(socket, bufferedWriter, bufferedReader);
        }
    }

    public void connectToServer() {
        sendMessage(nickname);
        listenForMessage();
    }

// TODO: Currently
    public void listenForMessage() {
        new Thread(() -> {
            String serverMessage;
            while (socket.isConnected()) {
                try {
                    serverMessage = bufferedReader.readLine();
                    if (serverMessage != null) {
                        messageQueue.put(serverMessage);
                    }
                } catch (IOException | InterruptedException e) {
                    closeEverything(socket, bufferedWriter, bufferedReader);
                }
            }
        }).start();
    }

    private void processMessages() {
        new Thread(() -> {
            while (true) {
                try {
                    String serverMessage = messageQueue.take();
                    handleServerMessage(serverMessage);
                } catch (InterruptedException | IOException e) {
                    e.printStackTrace();
                }
            }
        }).start();
    }

    // TODO: Continue working on this. It is stuck in a loop of HMIYes, and will constantly send "ReadytoRecv" to the server.
    private void handleServerMessage(String serverMsg) throws IOException {
        System.out.println("Server: " + serverMsg);
        switch (serverMsg) {
            case "HMIYes":
                sendMessage("ReadytoRecv");
                break;
            case "ServerSENDDone":
                break;
            case "ServerReady":
                // TODO: Implement sending JSON back to server
                break;
            case "pass":
                break;
            default:
                if (serverMsg.startsWith("{") && serverMsg.endsWith("}")) { // Assuming JSON data starts with '{' and ends with '}'
                    jsonMessageHandler.writeStringToMap(serverMsg);
                    sendMessage("ClientSENDDone");
                    sendMessage("pass");
                }
                break;
        }
    }

    //TODO: end up removing this method after testing.
    /**
     * Used to test getting Updates.
     * Use this in conjunction with the GUI to check getting HMI updated values.
     */
    private void getUpdateInLoop() {
        new Thread(() -> {
            while (true) {
                sendMessage("HMINew");
                try {
                    Thread.sleep(2000);
                } catch (InterruptedException e) {
                    e.printStackTrace();
                }
            }
        }).start();
    }

    public void closeEverything(Socket socket, BufferedWriter bufferedWriter, BufferedReader bufferedReader) {
        try {
            if (socket != null) {
                socket.close();
            }
            if (bufferedWriter != null) {
                bufferedWriter.close();
            }
            if (bufferedReader != null) {
                bufferedReader.close();
            }
        } catch (IOException e) {
            e.printStackTrace();
        }
    }

    public static void main(String[] args) throws IOException {
        Socket socket = new Socket("127.0.0.1", 55556);
        ClientController clientController = new ClientController(socket);
        clientController.connectToServer();
        clientController.getUpdateInLoop();
    }
}