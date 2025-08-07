package org.example.Client;

import org.example.jsonOperator.service.JSONOperatorServiceStub;
import org.example.util.TestUtils;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.mockito.Mock;
import org.mockito.MockitoAnnotations;

import java.io.*;
import java.net.Socket;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;

import static org.mockito.Mockito.*;

class ClientControllerTest {

        @Mock
        private Socket socket;
        @Mock
        private BufferedReader bufferedReader;
        @Mock
        private BufferedWriter bufferedWriter;
        @Mock
        private JSONOperatorServiceStub jsonMessageHandler;

        private ClientController clientController;
        private AutoCloseable mocks;
        private ExecutorService singleThreadExecutor;

        @BeforeEach
        void setUp() throws IOException {
                mocks = MockitoAnnotations.openMocks(this);
                singleThreadExecutor = Executors.newSingleThreadExecutor();

                // Mock socket streams
                when(socket.getInputStream()).thenReturn(mock(InputStream.class));
                when(socket.getOutputStream()).thenReturn(mock(OutputStream.class));
                when(socket.isConnected()).thenReturn(true);

                // Instantiate the controller with mocks
                clientController = new ClientController(socket, jsonMessageHandler);

                // Replace internal reader/writer with mocks for easier testing
                clientController.bufferedReader = bufferedReader;
                clientController.bufferedWriter = bufferedWriter;
        }

        @AfterEach
        void tearDown() throws Exception {
                mocks.close();
                singleThreadExecutor.shutdownNow();
        }

        @Test
        void testReceivePassMessage() throws IOException, InterruptedException {
                when(bufferedReader.readLine()).thenReturn("pass", (String) null);

                clientController.listenForMessage();

                // Allow the listening thread to process the message
                Thread.sleep(100);

                verify(bufferedWriter).write("HMINew\n");
                verify(bufferedWriter).flush();
        }

        @Test
        void testReceiveHMINoMessage() throws IOException, InterruptedException {
                when(bufferedReader.readLine()).thenReturn("HMINo", (String) null);

                clientController.listenForMessage();
                Thread.sleep(100);

                verify(bufferedWriter).write("HMINew\n");
        }

        @Test
        void sendAllJSONToMap() throws IOException, InterruptedException {
                String jsonData = TestUtils.readJsonFile("fullDBTest.json");
                when(bufferedReader.readLine()).thenReturn(jsonData, (String) null);

                clientController.listenForMessage();
                Thread.sleep(100);

                verify(jsonMessageHandler).writeStringToMap(jsonData);
        }

        @Test
        void testReceiveHMIYesMessage() throws IOException, InterruptedException {
                when(bufferedReader.readLine()).thenReturn("HMIYes", (String) null);

                clientController.listenForMessage();
                Thread.sleep(100);

                verify(bufferedWriter).write("ReadytoRecv\n");
                verify(bufferedWriter).flush();
        }

        @Test
        void testHandleConnectionError() throws IOException {
                doThrow(new IOException("Connection lost")).when(bufferedWriter).write(anyString());

                clientController.sendMessage("test");

                verify(socket, timeout(100)).close();
                verify(bufferedReader, timeout(100)).close();
                verify(bufferedWriter, timeout(100)).close();
        }

        @Test
        void testInitialConnection() throws IOException {
                clientController.connectToServer();

                verify(bufferedWriter, timeout(100)).write("HMI\n");
                verify(bufferedWriter, timeout(100)).flush();
        }
}