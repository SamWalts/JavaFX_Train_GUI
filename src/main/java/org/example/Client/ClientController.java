package org.example.Client;

import java.io.*;
import java.net.Socket;
import java.nio.charset.StandardCharsets;
import java.util.Scanner;

public class ClientController {

    private Socket socket;
    private BufferedReader bufferedReader;
    private InputStreamReader inputStreamReader;
    private BufferedWriter bufferedWriter;
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

    /**
     * Sends messages to the server
     * @param message
     */
    public void sendMessage(String message) {
        try {
            if (socket.isConnected()) {
                bufferedWriter.write(message);
                bufferedWriter.flush();
            }
        } catch (IOException e) {
            closeEverything(socket, bufferedWriter, bufferedReader);
        }
    }

    public void makeMessage() {
        Scanner scanner = new Scanner(System.in);
        boolean SendEntireDBb = false;
        boolean SendUpdateDBb = false;

        sendMessage(nickname);
        while (true) {
            try {
                Thread.sleep(67);
            } catch (InterruptedException e) {
                e.printStackTrace();
            }

            System.out.println("New data?, PISendingUpdate, PIReadytoRecv, ServerSendEntiretoPI, ServerSendUpdatestoP, Zero");
            System.out.println("1=PINew?, 2=Send, 3=PIReadytoRecv, 4=Entire, 5=Updates, 6=Zero, 7=Print ");
            int x = scanner.nextInt();

            switch (x) {
                case 1: // Is there new data?
                    sendMessage("PINew");
                    break;

                case 2: // SEND PI UPDATES TO SERVER
//                    LocalUpdate(); // update selected variable
                    sendMessage("HMISendingUpdate");
//                    try {
//                        Thread.sleep(50);
//                    } catch (InterruptedException e) {
//                        e.printStackTrace();
//                    }
//                    // pull PIdb rows values
//                    int HMI_Readi = Xsend; // Assuming Xsend is defined elsewhere
//                    String PItoServerUpdateSend = GetValuesforServer(HMI_Readi);
//                    sendMessage(PItoServerUpdateSend);
//                    try {
//                        Thread.sleep(50);
//                    } catch (InterruptedException e) {
//                        e.printStackTrace();
//                    }
                    break;

                case 3: // HMI ready for receive
                    sendMessage("HMIReadytoRecv");
//                    try {
//                        Thread.sleep(50);
//                    } catch (InterruptedException e) {
//                        e.printStackTrace();
//                    }
//                    if (SendEntireDBb) {
//                        PIdb.purge(); // Replace PI's Tinydb with server's
//                        SendEntireDBb = false;
//                        // parse its JSON
//                        List<Map<String, Object>> json_data = json.loads(svrmsg);
//                        for (Map<String, Object> entry : json_data) {
//                            PIdb.insert(entry); // insert it in the DB
//                        }
//                    }
//                    if (SendUpdateDBb) {
//                        while (svrmsg.equals("Connected to server!")) { // wait
//                            System.out.println("Waiting on server update");
//                            try {
//                                Thread.sleep(50);
//                            } catch (InterruptedException e) {
//                                e.printStackTrace();
//                            }
//                            if (!svrmsg.equals("No Update Available")) {
//                                PIdbUpdate(svrmsg);
//                                SendUpdateDBb = false;
//                            } else {
//                                System.out.println(svrmsg);
//                            }
//                        }
//                    }
                    break;

                case 4: // PI requests the entire DB
                    SendEntireDBb = true;
                    SendUpdateDBb = false;
                    sendMessage("ServerSendEntiretoHMI");
                    System.out.println("Select 3 to execute command");
                    break;

                case 5: // PI requests only updates in PIdb
                    sendMessage("ServerSendUpdatestoHMI");
                    SendEntireDBb = false;
                    SendUpdateDBb = true;
                    System.out.println("Select 3 to execute command");
                    break;

                case 6: // Zero PI DB
//                    PIdb.update("HMI_READi", 0); // sets all values to 0 in column "HMI_READi"
//                    System.out.println(PIdb.size());
                    break;

                case 7: // print PIDB
                    System.out.println("\nPRINT HMIdb\n ");
//                    for (Map<String, Object> row : PIdb) {
//                        System.out.println(row);
//                    }
//                    System.out.println(PIdb.size());
                    break;

                default:
                    System.out.println("Select 1 through 7 only!"); // out of range
                    break;
            }
        }
    }

    public void listenForMessage() {
        new Thread(() -> {
            String serverMessage;
            while (socket.isConnected()) {
                try {
                    serverMessage = bufferedReader.readLine();
                    System.out.println('\n' + serverMessage);
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
        String nickname = "HMI";
        if (nickname == null || nickname.isEmpty()) {
            System.out.println("Username cannot be null or empty.");
            return;
        }
        Socket socket = new Socket("127.0.0.1", 55555);
        Client client = new Client(socket, nickname);
        client.listenForMessage();
        client.makeMessage();
    }
}