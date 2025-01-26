package org.example.Client;

import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.mockito.Mockito;

import java.io.*;
import java.net.Socket;

import static org.mockito.Mockito.*;

public class ClientControllerTest {

    private Socket socket;
    private BufferedReader bufferedReader;
    private BufferedWriter bufferedWriter;
    private ClientController clientController;

    @BeforeEach
    public void setUp() throws IOException {
        socket = mock(Socket.class);
        bufferedReader = mock(BufferedReader.class);
        bufferedWriter = mock(BufferedWriter.class);

        when(socket.getInputStream()).thenReturn(mock(InputStream.class));
        when(socket.getOutputStream()).thenReturn(mock(OutputStream.class));

        clientController = new ClientController(socket, "HMI");
        clientController.bufferedReader = bufferedReader;
        clientController.bufferedWriter = bufferedWriter;
    }

    @Test
    public void testReadMessage() throws IOException {
        String testMessage = "Test message from server";
        when(bufferedReader.readLine()).thenReturn(testMessage);

        clientController.readMessage(testMessage);

        verify(bufferedReader, times(1)).readLine();
        System.out.println("Test passed: Message received correctly");
    }
}