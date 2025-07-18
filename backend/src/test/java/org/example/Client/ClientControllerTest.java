package org.example.Client;

import org.example.jsonOperator.service.JSONOperatorServiceStub;
import org.example.util.TestUtils;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import java.io.*;
import java.net.Socket;

import static org.mockito.Mockito.*;


class ClientControllerTest {
        private Socket socket;
        private BufferedReader bufferedReader;
        private BufferedWriter bufferedWriter;
        private ClientController clientController;

        @BeforeEach
        void setUp() throws IOException {
                // Setup mocks
                socket = mock(Socket.class);
                bufferedReader = mock(BufferedReader.class);
                bufferedWriter = mock(BufferedWriter.class);

                // Configure socket mock
                when(socket.getInputStream()).thenReturn(mock(InputStream.class));
                when(socket.getOutputStream()).thenReturn(mock(OutputStream.class));
                when(socket.isConnected()).thenReturn(true);

                when(bufferedReader.ready()).thenReturn(true, false);

                // Create controller with mocked components
                clientController = new ClientController(socket);
                clientController.bufferedReader = bufferedReader;
                clientController.bufferedWriter = bufferedWriter;
        }

        @Test
        void testReceivePassMessage() throws IOException, InterruptedException {
                // Setup
                when(bufferedReader.readLine())
                        .thenReturn("pass")
                        .thenReturn(null);

                // Execute
                clientController.listenForMessage();
                // Verify
                verify(bufferedWriter, timeout(100)).write("HMINew" + "\n");
                verify(bufferedWriter, timeout(100)).flush();
        }

        @Test
        void testReceiveHMINoMessage() throws IOException, InterruptedException {
                // Setup
                when(bufferedReader.readLine())
                        .thenReturn("HMINo")
                        .thenReturn(null);

                // Execute
                clientController.listenForMessage();
                // Verify
                verify(bufferedWriter, timeout(100)).write("HMINew" + "\n");
        }

        @Test
        void sendAllJSONToMap() throws IOException, InterruptedException {
                String jsonData = TestUtils.readJsonFile("fullDBTest.json");
                when(bufferedReader.readLine())
                        .thenReturn(jsonData)
                        .thenReturn(null);

                JSONOperatorServiceStub serviceSpy = spy(new JSONOperatorServiceStub());
                clientController.setJsonMessageHandler(serviceSpy);

                clientController.listenForMessage();
                Thread.sleep(50);
//              Verify that the correct method is called when client encounters JSON Data
                verify(serviceSpy).writeStringToMap(jsonData);
        }

        @Test
        void testReceiveHMIYesMessage() throws IOException, InterruptedException {
                // Setup
                when(bufferedReader.readLine())
                        .thenReturn("HMIYes")
                        .thenReturn(null);

                // Execute
                clientController.listenForMessage();
                Thread.sleep(50);
                // Verify
                verify(bufferedWriter).write("ReadytoRecv" + "\n");
                verify(bufferedWriter).flush();
        }

//        TODO: Failing, not sure why, need to investigate
        @Test
        void testReceiveServerSENDDoneMessage() throws IOException, InterruptedException {
                // Setup
                when(bufferedReader.readLine())
                        .thenReturn("ServerSENDDone")
                        .thenReturn(null);

                // Execute
                clientController.listenForMessage();
//                Thread.sleep(50);
                // Verify
                verify(bufferedWriter).write("ClientSENDDone" + "\n");
                verify(bufferedWriter).flush();
        }

        @Test
        void testHandleConnectionError() throws IOException, InterruptedException {
                // Setup
                doThrow(new IOException()).when(bufferedWriter).write(anyString());

                // Execute
                clientController.sendMessage("test");
                Thread.sleep(50);
                // Verify cleanup
                verify(socket).close();
                verify(bufferedReader).close();
                verify(bufferedWriter).close();
        }

        @Test
        void testInitialConnection() throws IOException, InterruptedException {
                // Execute
                clientController.connectToServer();
                Thread.sleep(50);
                // Verify
                verify(bufferedWriter).write("HMI" + "\n");
                verify(bufferedWriter).flush();

        }
}