package org.example.Client;

import java.io.*;
import java.net.Socket;
import java.nio.charset.StandardCharsets;
import java.util.concurrent.*;

import org.example.jsonOperator.service.JSONOperatorServiceStub;

public class ClientController {

    private static ClientController instance;
    private Socket socket;
    BufferedReader bufferedReader;
    BufferedWriter bufferedWriter;
    JSONOperatorServiceStub jsonMessageHandler;
    private BlockingQueue<String> messageQueue;

    private String nickname = "HMI";
    private final ScheduledExecutorService scheduler = Executors.newScheduledThreadPool(1);


    /**
     * Constructor for the ClientController.
     * @param socket connection to the server.
     */
    public ClientController(Socket socket) {
        try {
            this.socket = socket;
            this.bufferedReader = new BufferedReader(new InputStreamReader(socket.getInputStream(), StandardCharsets.UTF_8));
            this.bufferedWriter = new BufferedWriter(new OutputStreamWriter(socket.getOutputStream(), StandardCharsets.UTF_8));
            this.jsonMessageHandler = new JSONOperatorServiceStub();
            this.messageQueue = new LinkedBlockingQueue<>();
            processMessages();

            instance = this; // Set the singleton instance to this controller
        } catch (IOException e) {
            closeEverything(socket, bufferedWriter, bufferedReader);
        }
    }

    // Add a static initialization method for use at application startup
    public static synchronized void initializeInstance() throws IOException {
        if (instance == null) {
            Socket socket = new Socket("127.0.0.1", 55556);
            instance = new ClientController(socket);
            instance.connectToServer();
        }
    }

    // Fix the getInstance method
    public static synchronized ClientController getInstance() {
        // It will return the existing instance or null if none exists
        if (instance == null) {
            try {
                initializeInstance(); // Initialize if not already done
            } catch (IOException e) {
                e.printStackTrace();
                return null; // Return null if initialization fails
            }
        }
        return instance;
    }

    /**
     * Set the JSON message handler.
     * @param handler JSONOperatorServiceStub
     */
    public void setJsonMessageHandler(JSONOperatorServiceStub handler) {
        this.jsonMessageHandler = handler;
    }

    /**
     * Send a message to the server.
     * @param message to send it to the server.
     */
    public void sendMessage(String message) {
        if (message.equals("HMINew")) {
            // Do nothing, this is just a poll message.
        }
        else {
            System.out.println("Client: " + message);
        }
        try {
            if (socket.isConnected()) {
                bufferedWriter.write(message + "\n");
                bufferedWriter.flush();
            }
        } catch (IOException e) {
            closeEverything(socket, bufferedWriter, bufferedReader);
        }
    }

    /**
     * Connect to the server.
     */
    public void connectToServer() {
        sendMessage(nickname);
        listenForMessage();
        startPollingServer();
    }

    /**
     * Starts a scheduled task to poll the server for updates periodically.
     * It sends "paulNew" and waits for the server's response, which is
     * handled by the message listener.
     */
    public void startPollingServer() {
        // Poll the server every second, starting after a 1-second delay.
        scheduler.scheduleAtFixedRate(() -> {
            sendMessage("HMINew");
        }, 1, 1, TimeUnit.SECONDS);
    }

    /**
     * Listens for messages from the server.
     */
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

    /**
     * Processes messages from the server in a new thread for non blocking.
     * Accesses the message from the messageQueue,.
     */
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

    /**
     * Handles messages from the server.
     * @param serverMsg message from the server.
     * @throws IOException if there is an issue with the input/output.
     */
    private void handleServerMessage(String serverMsg) throws IOException {
//        System.out.println("Server: " + serverMsg);
        switch (serverMsg) {
            case "HMIYes":
                sendMessage("ReadytoRecv");
                break;
            case "ServerSENDDone":
                break;
//                If the server is ready, send the JSON data.
            case "ServerReady":
                if (jsonMessageHandler.hasUpdatedHMI_READi()) {
                    // Check if the method getHmiJsonDao() is just null or if it does anything...
                    String JSONToSend = jsonMessageHandler.getStringToSendToServer(jsonMessageHandler.getHmiDataMap());
                    sendMessage(JSONToSend);
                }
                break;
            case "pass", "HMINo":
//                Ask server if new messages are available
                sendMessage("HMINew");
                break;
            default:
//                Default will always deal with the JSON data.
                if (serverMsg.startsWith("[{") || serverMsg.startsWith("{")) { // Check for both array and object JSON
                    jsonMessageHandler.writeStringToMap(serverMsg);
                    break;
                }
                break;
        }
    }

    /**
     *  Close the socket, bufferedWriter, and bufferedReader.
     * @param socket connection to the server.
     * @param bufferedWriter to write to the server.
     * @param bufferedReader to read from the server.
     */
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
    }
}