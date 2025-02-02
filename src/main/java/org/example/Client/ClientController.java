package org.example.Client;

import java.io.*;
import java.net.Socket;
import java.nio.charset.StandardCharsets;
//TODO: check if handleHMI should be the same as handlePaul from the server side.
public class ClientController {

    private Socket socket;
    BufferedReader bufferedReader;
    private InputStreamReader inputStreamReader;
    BufferedWriter bufferedWriter;
    private final String nickname = "HMI";
    private String ServersendingUpdatesb, PIdb;

    public ClientController(Socket socket) {
        try {
            this.socket = socket;
            this.bufferedReader = new BufferedReader(new InputStreamReader(socket.getInputStream(), StandardCharsets.UTF_8));
            this.inputStreamReader = new InputStreamReader(socket.getInputStream(), StandardCharsets.UTF_8);
            this.bufferedWriter = new BufferedWriter(new OutputStreamWriter(socket.getOutputStream(), StandardCharsets.UTF_8));
        } catch (IOException e) {
            closeEverything(socket, bufferedWriter, bufferedReader);
        }
    }

    public void handleHMI() {
        String serverMessage;
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

    public void sendMessage() {
        boolean SendEntireDBb = false;
        boolean SendUpdateDBb = false;

        sendMessage(nickname);
        listenForMessage();
    }

    public void listenForMessage() {
        new Thread(() -> {
            String serverMessage;
            while (socket.isConnected()) {
                try {
                    serverMessage = bufferedReader.readLine();
                    if (serverMessage != null) {
                        readMessage(serverMessage);
                    }
                } catch (IOException e) {
                    closeEverything(socket, bufferedWriter, bufferedReader);
                }
            }
        }).start();
    }

    public void readMessage(String serverMsg) {
        System.out.println("Server: " + serverMsg);
        handleServerMessage(serverMsg);
    }
// TODO: Change this at some point to be a loop for reading in and dynamically handling messages
    private void handleServerMessage(String serverMsg) {
        if (serverMsg.equals("NICK")) {
            connectToServer();
        }
        if (serverMsg.equals("HMIYes")) {
            getHMIDataFromServer();
//            TODO: Do I need this?
            if (serverMsg.equals("HMINo")) {
                sendMessage("HMIDone");
            }
            decodeJSONFromServer(serverMsg);
            // read into json format, and get decoded on JSONMessageHandler.java
        }
    }

//  TODO: Implement this method
    private void decodeJSONFromServer(String serverMessage) {
        System.out.println("Getting HMI Data from Server");
    }

    private void getHMIDataFromServer() {
        System.out.println("Getting HMI Data from Server");
        sendMessage("HMIReadytoRecv");
    }
//  TODO: Add error handling for connection to server
    private void connectToServer() {
        sendMessage(nickname);
    }
    /*
    Psuedocode for getting information from the server, and which messages to send/ wait for
    1. Send nickname to server

    2. Wait for server to send "pass" message

    Options to send:
        1. HMINew
            IF HMIReadytoRecv
                will sleep for .050 ms
            IF HMIReadytoRecv
                Will get LocalUpdate from JSONDB
                WILL DUMP ALL JSON DATA to HMI
        2. HMIDone
            Will get HMINo
        3. HMISendingUpdate
            MUST GET ServerReadytoRecv
        4. send Print Server.
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
        clientController.listenForMessage();
        clientController.sendMessage();
        clientController.sendMessage("HMINew");
//        clientController.sendMessage("HMIReadytoRecv");
    }
}