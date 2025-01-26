package org.example.Client;

import java.io.*;
import java.net.Socket;
import java.nio.charset.StandardCharsets;

public class ClientController {

    private Socket socket;
    BufferedReader bufferedReader;
    private InputStreamReader inputStreamReader;
    BufferedWriter bufferedWriter;
    private String nickname;
    private String ServersendingUpdatesb, PIdb;

    public ClientController(Socket socket, String nickname) {
        try {
            this.socket = socket;
            this.bufferedReader = new BufferedReader(new InputStreamReader(socket.getInputStream(), StandardCharsets.UTF_8));
            this.inputStreamReader = new InputStreamReader(socket.getInputStream(), StandardCharsets.UTF_8);
            this.bufferedWriter = new BufferedWriter(new OutputStreamWriter(socket.getOutputStream(), StandardCharsets.UTF_8));
            this.nickname = nickname;
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

    public void readMessage(String message) {
        System.out.println("Server: " + message);
        parseMessage(message);
    }

    public void parseMessage(String serverMessage) {
        System.out.println(serverMessage + " is the message");
        switch (serverMessage) {
            case "pass":
                System.out.print("serverMessage");
                break;
            case "HMISendingUpdate":
                System.out.println("Sending update to server");
                break;
            case "HMIReadytoRecv":
                System.out.println("Ready to receive");
                break;
            case "ServerSendEntiretoHMI":
                System.out.println("Server sending entire DB to HMI");
                break;
            case "ServerSendUpdatestoHMI":
                System.out.println("Server sending updates to HMI");
                break;
            case "Zero":
                System.out.println("Zeroing out HMI_READi column");
                break;
            default:
                System.out.println("Unknown message: " + serverMessage);
        }
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
        String nickname = "HMI";
        if (nickname == null || nickname.isEmpty()) {
            System.out.println("Username cannot be null or empty.");
            return;
        }
        Socket socket = new Socket("127.0.0.1", 55556);
        ClientController clientController = new ClientController(socket, nickname);
        clientController.listenForMessage();
        clientController.sendMessage();
        clientController.sendMessage("HMINew");
        clientController.sendMessage("HMIReadytoRecv");
    }
}