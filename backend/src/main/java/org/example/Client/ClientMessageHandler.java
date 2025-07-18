package org.example.Client;

import org.example.jsonOperator.dto.HmiData;
import java.io.IOException;
import java.util.List;

/**
 * Interface for handling client-server communication in the train control system.
 * Defines methods for checking updates, receiving data, and sending changes to the server.
 */
public interface ClientMessageHandler {

    /**
     * Checks if there are any updates available from the server.
     *
     * @return true if updates are available, false otherwise
     * @throws IOException if communication error occurs
     */
    boolean checkForUpdates() throws IOException;

    /**
     * Requests and receives updated data from the server.
     *
     * @return List of updated HmiData objects
     * @throws IOException if communication error occurs
     */
    List<HmiData> receiveUpdates() throws IOException;

    /**
     * Sends updated data to the server.
     *
     * @param updates List of HmiData objects to be sent to the server
     * @throws IOException if communication error occurs
     */
    void sendUpdates(List<HmiData> updates) throws IOException;

    /**
     * Connects to the server and initializes the communication.
     *
     * @return true if connection was successful, false otherwise
     * @throws IOException if connection error occurs
     */
    boolean connect() throws IOException;

    /**
     * Disconnects from the server and cleans up resources.
     *
     * @throws IOException if disconnection error occurs
     */
    void disconnect() throws IOException;

    /**
     * Requests the server to print its current state (debug feature).
     *
     * @throws IOException if communication error occurs
     */
    void requestServerPrint() throws IOException;
}