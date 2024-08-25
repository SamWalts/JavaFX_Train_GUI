/**
 * This is a simple server program that listens to a port and accepts connections from clients.
 * The server reads messages from the client and sends a response back to the client.
 * The server will keep listening to the client until the client sends an "exit" message.
 * The server will close the connection and wait for another client to connect.
 */

package org.example.Client;

import java.io.*;
import java.net.ServerSocket;
import java.net.Socket;

public class ServerTest {

    public static void main(String[] args) throws IOException {
        Socket socket = null;
        ServerSocket serverSocket = null;
        InputStreamReader inputStreamReader = null;
        OutputStreamWriter outputStreamWriter = null;
        BufferedReader bufferedReader = null;
        BufferedWriter bufferedWriter = null;

        serverSocket = new ServerSocket(1234);

        while (true) {

            try{
                socket = serverSocket.accept();
                inputStreamReader = new InputStreamReader(socket.getInputStream());
                outputStreamWriter = new OutputStreamWriter(socket.getOutputStream());

                bufferedReader = new BufferedReader(inputStreamReader);
                bufferedWriter = new BufferedWriter(outputStreamWriter);

                while(true) {

                    String msgFromClient = bufferedReader.readLine();
                    System.out.println("Message from client: " + msgFromClient);

                    bufferedWriter.write("Message received " + msgFromClient);
                    bufferedWriter.newLine();
                    bufferedWriter.flush();

                    if (msgFromClient.equalsIgnoreCase("exit")) {
                        break;
                    }

                }
            } catch (IOException e) {
                e.printStackTrace();
            } finally {
                if (socket != null) {
                    socket.close();
                }
                if (inputStreamReader != null) {
                    inputStreamReader.close();
                }
                if (outputStreamWriter != null) {
                    outputStreamWriter.close();
                }
                if (bufferedReader != null) {
                    bufferedReader.close();
                }
                if (bufferedWriter != null) {
                    bufferedWriter.close();
                }

            }
        }
    }
}
