package org.example.Client;

import org.example.jsonOperator.service.JSONOperatorServiceStub;
import java.io.*;
import java.net.Socket;
import java.nio.charset.StandardCharsets;
import java.util.concurrent.*;

public class ClientController implements IClientController {

    private final Socket socket;
    protected BufferedReader bufferedReader;
    BufferedWriter bufferedWriter;
    private JSONOperatorServiceStub jsonMessageHandler;
    private final BlockingQueue<String> messageQueue;
    private final String nickname = "HMI";
    private final ScheduledExecutorService scheduler = Executors.newScheduledThreadPool(1);

    /**
     * Constructor for the ClientController.
     * @param socket connection to the server.
     * @param jsonMessageHandler handler for JSON messages.
     */
    public ClientController(Socket socket, JSONOperatorServiceStub jsonMessageHandler) throws IOException {
        this.socket = socket;
        this.bufferedReader = new BufferedReader(new InputStreamReader(socket.getInputStream(), StandardCharsets.UTF_8));
        this.bufferedWriter = new BufferedWriter(new OutputStreamWriter(socket.getOutputStream(), StandardCharsets.UTF_8));
        this.jsonMessageHandler = jsonMessageHandler;
        this.messageQueue = new LinkedBlockingQueue<>();
        processMessages();
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
     * It sends "HMINew" and waits for the server's response, which is
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
     * Accesses the message from the messageQueue.
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
                jsonMessageHandler.finalizeSentData();
                break;
//                If the server is ready, send the JSON data.
            case "ServerReady":
                if (jsonMessageHandler.hasUpdatedHMI_READi()) {
                    // Build a batch and track in-flight keys, then send JSON and finish handshake
                    String payload = jsonMessageHandler.prepareDataForSending();
                    if (payload != null && !payload.equals("[]")) {
                        sendMessage(payload);
                        sendMessage("ClientSENDDone");
                    }
                }
                break;
            case "pass":
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

    static void main(String[] args) throws IOException {
        Socket socket = new Socket("127.0.0.1", 55556);
        // Fix: Provide the JSONOperatorServiceStub dependency
        JSONOperatorServiceStub jsonHandler = new JSONOperatorServiceStub();
        ClientController clientController = new ClientController(socket, jsonHandler);
        clientController.connectToServer();
    }
}