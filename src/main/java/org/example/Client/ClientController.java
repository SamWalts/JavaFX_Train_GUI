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
    JSONOperatorServiceStub jsonMessageHandler;
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

//   check if the setter used in tests?
    public void setJsonMessageHandler(JSONOperatorServiceStub handler) {
        this.jsonMessageHandler = handler;
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

//    TODO: Work on the python portion.
    private void handleServerMessage(String serverMsg) throws IOException {
        System.out.println("Server: " + serverMsg);
        switch (serverMsg) {
            case "HMIYes":
                sendMessage("ReadytoRecv");
                break;
            case "ServerSENDDone":
                sendMessage("TEST");
                break;
            case "ServerReady":
                // TODO: Implement sending JSON back to server
                break;
            case "pass", "HMINo":
                sendMessage("HMINew");
                // if listenermap contains items where hmireadi > 2
                // aend message "SendingUpdates"
                // else send message "NoUpdates"        
                // send message "pass"
                // if Servermsg is ServerReady
                    // get all json where hmireadi > 2
                    //send all
                        // TODO: handle reaetting the hmireqdi here or on the jsonoperator


//                TODO: Implement the Python method into Java here
//                elif svrmsg == "paulNo":
//                if GUIdb.count(query.HMI_READi > 0) > 0:
//                message = "SendingUpdates"
//                client.send(message.encode(FORMAT))
//                sleep(0.100)
//            else: # nothing to send
//                    message = "\n NoUpdates"
//                client.send(message.encode(FORMAT))
//                sleep(0.100)
//                message = "pass"
//                client.send(message.encode(FORMAT))
//                elif svrmsg == "ServerReady":
//                print("in server ready section")
//                ToZeroHMI_READi = GUIdb.search(query.HMI_READi > 0)
//                message = json.dumps(ToZeroHMI_READi)
//                client.send(message.encode(FORMAT)) # send updates
//                print("GUI sent to Server: ", message)
//                sleep(0.700)
//                client.send("ClientSENDDone".encode(FORMAT))
//                for row  in ToZeroHMI_READi: # ** SET HMI_READi TO 0 **
//                    ToZeroHMI_READiIndex = row.get("INDEX")
//                GUIdb.update({"HMI_READi": 0}, query.INDEX == ToZeroHMI_READiIndex)

            default:
                if (serverMsg.startsWith("[{") || serverMsg.startsWith("{")) { // Check for both array and object JSON
                    jsonMessageHandler.writeStringToMap(serverMsg);
                    break;
                }
                break;
        }
    }

//    //TODO: end up removing this method after testing? Or keep it to continually look for new updates?
//    /**
//     * Used to test getting Updates.
//     * Use this in conjunction with the GUI to check getting HMI updated values.
//     */
//    private void getUpdateInLoop() {
//        new Thread(() -> {
//            while (true) {
//                sendMessage("HMINew");
//                try {
//                    Thread.sleep(2000);
//                } catch (InterruptedException e) {
//                    e.printStackTrace();
//                }
//            }
//        }).start();
//    }

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
//        clientController.getUpdateInLoop();
    }
}