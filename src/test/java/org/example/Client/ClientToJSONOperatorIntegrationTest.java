package org.example.Client;

import org.example.jsonOperator.service.JSONOperatorServiceStub;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.mockito.Mock;
import org.mockito.MockitoAnnotations;

import java.io.*;
import java.net.Socket;
import java.util.HashMap;

import static org.mockito.Mockito.*;
import static org.junit.jupiter.api.Assertions.*;

class ClientToJSONOperatorIntegrationTest {

    private Socket socket;
    private BufferedReader bufferedReader;
    private BufferedWriter bufferedWriter;
    private ClientController clientController;
    private JSONOperatorServiceStub jsonOperatorServiceStub;

//  TODO: Implement mocking for JSONOperatorServiceStub
    @BeforeEach
    void setUp() throws IOException {
        socket = mock(Socket.class);
        bufferedReader = mock(BufferedReader.class);
        bufferedWriter = mock(BufferedWriter.class);

        when(socket.getInputStream()).thenReturn(mock(InputStream.class));
        when(socket.getOutputStream()).thenReturn(mock(OutputStream.class));
        when(socket.isConnected()).thenReturn(true);

        clientController = new ClientController(socket);
        clientController.bufferedWriter = bufferedWriter;
        clientController.bufferedReader = bufferedReader;

    }
//    TODO: Implement mocking for ClientController

//    TODO: Test for parsing the whole JSON to hashmap.

//    TODO: Test for adding in single line change.
//    Must test for the following:


//    TODO: Test
}
