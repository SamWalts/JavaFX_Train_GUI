package org.example.Client;

import java.io.*;
import java.net.Socket;
import java.nio.charset.StandardCharsets;
import java.util.Scanner;

public class Client {

    private Socket socket;
    private BufferedReader bufferedReader;
    private InputStreamReader inputStreamReader;
    private BufferedWriter bufferedWriter;
    private String nickname;

    public Client(Socket socket, String nickname) {
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

    public void sendMessage() {
        try {
            if (nickname != null) {
                bufferedWriter.write(nickname);
                bufferedWriter.newLine();
                bufferedWriter.flush();
            } else {
                System.out.println("Nickname is null. Cannot send message.");
                return;
            }

            Scanner scanner = new Scanner(System.in);
            while (socket.isConnected()) {
                String message = scanner.nextLine();
                bufferedWriter.write(message);
                bufferedWriter.newLine();
                bufferedWriter.flush();
            }
        } catch (IOException e) {
            closeEverything(socket, bufferedWriter, bufferedReader);
        }
    }

    public void listenForMessage() {
        new Thread(() -> {
            String msgFromGroupChat;
            while (socket.isConnected()) {
                try {
                    msgFromGroupChat = bufferedReader.readLine();
//                    msgFromGroupChat = inputStreamReader.read() + "";
//                    TODO: add in some type of message handling here. I am missing some sort newline or something.
                        System.out.println("\n" + msgFromGroupChat);


                } catch (IOException e) {
                    closeEverything(socket, bufferedWriter, bufferedReader);
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

        String nickname = "PI";
        if (nickname == null || nickname.isEmpty()) {
            System.out.println("Username cannot be null or empty.");
            return;
        }
        Socket socket = new Socket("127.0.0.1", 55555);
        Client client = new Client(socket, nickname);
        client.listenForMessage();
        client.sendMessage();
    }
}