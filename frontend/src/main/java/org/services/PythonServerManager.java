package org.services;

import java.io.BufferedReader;
import java.io.File;
import java.io.IOException;
import java.io.InputStreamReader;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.logging.Level;
import java.util.logging.Logger;

/**
 * Singleton service that manages the Python server process lifecycle.
 * This service starts the server20a-test.py Python server when the JavaFX application starts
 * and ensures it is properly shutdown when the application exits.
 */
public class PythonServerManager {
    private static final Logger LOGGER = Logger.getLogger(PythonServerManager.class.getName());
    private static PythonServerManager instance;
    
    private Process serverProcess;
    private Thread outputThread;
    private Thread errorThread;
    private volatile boolean isRunning = false;
    
    private static final String SERVER_SCRIPT_NAME = "server20a-test.py";
    
    private PythonServerManager() {
        // Private constructor for singleton
    }
    
    /**
     * Returns the singleton instance of PythonServerManager.
     * 
     * @return The singleton instance of PythonServerManager.
     */
    public static synchronized PythonServerManager getInstance() {
        if (instance == null) {
            instance = new PythonServerManager();
        }
        return instance;
    }
    
    /**
     * Starts the Python server process.
     * The server script is located at backend/src/main/PythonScripts/server20a-test.py
     * 
     * @throws IOException if the server cannot be started
     */
    public synchronized void startServer() throws IOException {
        if (isRunning) {
            LOGGER.info("Python server is already running");
            return;
        }
        
        Path scriptPath = findServerScript();
        if (scriptPath == null || !Files.exists(scriptPath)) {
            throw new IOException("Python server script not found: " + SERVER_SCRIPT_NAME);
        }
        
        LOGGER.info("Starting Python server from: " + scriptPath.toAbsolutePath());
        
        ProcessBuilder processBuilder = new ProcessBuilder("python3", scriptPath.toString());
        processBuilder.directory(scriptPath.getParent().toFile());
        processBuilder.redirectErrorStream(false);
        
        try {
            serverProcess = processBuilder.start();
            isRunning = true;
            
            // Start threads to consume output and error streams to prevent blocking
            outputThread = new Thread(() -> consumeStream(serverProcess.getInputStream(), "OUTPUT"));
            errorThread = new Thread(() -> consumeStream(serverProcess.getErrorStream(), "ERROR"));
            
            outputThread.setDaemon(true);
            errorThread.setDaemon(true);
            
            outputThread.start();
            errorThread.start();
            
            LOGGER.info("Python server started successfully");
            
            // Add shutdown hook to ensure server is stopped when JVM exits
            Runtime.getRuntime().addShutdownHook(new Thread(() -> {
                try {
                    stopServer();
                } catch (Exception e) {
                    LOGGER.log(Level.WARNING, "Error stopping server in shutdown hook", e);
                }
            }));
            
        } catch (IOException e) {
            isRunning = false;
            LOGGER.log(Level.SEVERE, "Failed to start Python server", e);
            throw e;
        }
    }
    
    /**
     * Stops the Python server process gracefully.
     */
    public synchronized void stopServer() {
        if (!isRunning || serverProcess == null) {
            LOGGER.info("Python server is not running");
            return;
        }
        
        LOGGER.info("Stopping Python server...");
        
        try {
            // Try graceful shutdown first
            serverProcess.destroy();
            
            // Wait up to 5 seconds for graceful shutdown
            if (!serverProcess.waitFor(5, java.util.concurrent.TimeUnit.SECONDS)) {
                LOGGER.warning("Server did not stop gracefully, forcing shutdown");
                serverProcess.destroyForcibly();
            }
            
            LOGGER.info("Python server stopped successfully");
        } catch (InterruptedException e) {
            LOGGER.log(Level.WARNING, "Interrupted while stopping server", e);
            serverProcess.destroyForcibly();
            Thread.currentThread().interrupt();
        } finally {
            isRunning = false;
            serverProcess = null;
        }
    }
    
    /**
     * Checks if the server is currently running.
     * 
     * @return true if the server is running, false otherwise
     */
    public boolean isRunning() {
        return isRunning && serverProcess != null && serverProcess.isAlive();
    }
    
    /**
     * Finds the server script in the project structure.
     * Looks in backend/src/main/PythonScripts/ relative to the project root.
     * 
     * @return Path to the server script, or null if not found
     */
    private Path findServerScript() {
        // Try to find the script relative to the current working directory
        Path currentDir = Paths.get(System.getProperty("user.dir"));
        
        // Common locations to search
        Path[] searchPaths = {
            // When running from frontend module
            currentDir.resolve("../backend/src/main/PythonScripts/" + SERVER_SCRIPT_NAME),
            // When running from project root
            currentDir.resolve("backend/src/main/PythonScripts/" + SERVER_SCRIPT_NAME),
            // When running from target directory
            currentDir.resolve("../../backend/src/main/PythonScripts/" + SERVER_SCRIPT_NAME)
        };
        
        for (Path path : searchPaths) {
            try {
                Path normalized = path.normalize();
                if (Files.exists(normalized)) {
                    LOGGER.info("Found server script at: " + normalized.toAbsolutePath());
                    return normalized;
                }
            } catch (Exception e) {
                LOGGER.log(Level.FINE, "Error checking path: " + path, e);
            }
        }
        
        LOGGER.warning("Could not find server script: " + SERVER_SCRIPT_NAME);
        return null;
    }
    
    /**
     * Consumes an input stream and logs its content.
     * This prevents the process from blocking due to full output buffers.
     * 
     * @param inputStream The input stream to consume
     * @param streamType Type of stream (OUTPUT or ERROR) for logging
     */
    private void consumeStream(java.io.InputStream inputStream, String streamType) {
        try (BufferedReader reader = new BufferedReader(new InputStreamReader(inputStream))) {
            String line;
            while ((line = reader.readLine()) != null) {
                LOGGER.log(Level.INFO, "[Python Server " + streamType + "] " + line);
            }
        } catch (IOException e) {
            if (isRunning) {
                LOGGER.log(Level.WARNING, "Error reading " + streamType + " stream", e);
            }
        }
    }
}
