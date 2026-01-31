package org.services;

import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;

import static org.junit.jupiter.api.Assertions.*;

/**
 * Test class for PythonServerManager.
 * Tests the lifecycle management of the Python server process.
 */
class PythonServerManagerTest {

    private PythonServerManager serverManager;

    @BeforeEach
    void setUp() {
        serverManager = PythonServerManager.getInstance();
        // Ensure server is stopped before each test
        if (serverManager.isRunning()) {
            serverManager.stopServer();
        }
    }

    @AfterEach
    void tearDown() {
        // Cleanup: stop server after each test
        if (serverManager.isRunning()) {
            serverManager.stopServer();
        }
    }

    @Test
    void testGetInstance_returnsSameInstance() {
        PythonServerManager instance1 = PythonServerManager.getInstance();
        PythonServerManager instance2 = PythonServerManager.getInstance();
        assertSame(instance1, instance2, "getInstance should return the same singleton instance");
    }

    @Test
    void testStartServer_startsSuccessfully() throws IOException, InterruptedException {
        // Check if server script exists before trying to start
        Path scriptPath = findServerScript();
        if (scriptPath == null || !Files.exists(scriptPath)) {
            // Skip test if script is not found (may happen in CI environment)
            System.out.println("Skipping test: server script not found");
            return;
        }

        serverManager.startServer();
        
        // Give the server a moment to start
        Thread.sleep(1000);
        
        assertTrue(serverManager.isRunning(), "Server should be running after start");
    }

    @Test
    void testStartServer_alreadyRunning_doesNotStartAgain() throws IOException, InterruptedException {
        Path scriptPath = findServerScript();
        if (scriptPath == null || !Files.exists(scriptPath)) {
            System.out.println("Skipping test: server script not found");
            return;
        }

        serverManager.startServer();
        Thread.sleep(500);
        
        assertTrue(serverManager.isRunning(), "Server should be running");
        
        // Try to start again - should be idempotent
        serverManager.startServer();
        assertTrue(serverManager.isRunning(), "Server should still be running");
    }

    @Test
    void testStopServer_stopsRunningServer() throws IOException, InterruptedException {
        Path scriptPath = findServerScript();
        if (scriptPath == null || !Files.exists(scriptPath)) {
            System.out.println("Skipping test: server script not found");
            return;
        }

        serverManager.startServer();
        Thread.sleep(500);
        assertTrue(serverManager.isRunning(), "Server should be running");
        
        serverManager.stopServer();
        Thread.sleep(500);
        
        assertFalse(serverManager.isRunning(), "Server should not be running after stop");
    }

    @Test
    void testStopServer_whenNotRunning_doesNotThrowException() {
        // Should not throw exception
        assertDoesNotThrow(() -> serverManager.stopServer(),
                "Stopping a non-running server should not throw exception");
    }

    @Test
    void testIsRunning_initiallyFalse() {
        assertFalse(serverManager.isRunning(), "Server should not be running initially");
    }

    @Test
    void testServerLifecycle_startStopMultipleTimes() throws IOException, InterruptedException {
        Path scriptPath = findServerScript();
        if (scriptPath == null || !Files.exists(scriptPath)) {
            System.out.println("Skipping test: server script not found");
            return;
        }

        // First cycle
        serverManager.startServer();
        Thread.sleep(500);
        assertTrue(serverManager.isRunning(), "Server should be running after first start");
        
        serverManager.stopServer();
        Thread.sleep(500);
        assertFalse(serverManager.isRunning(), "Server should be stopped after first stop");
        
        // Second cycle
        serverManager.startServer();
        Thread.sleep(500);
        assertTrue(serverManager.isRunning(), "Server should be running after second start");
        
        serverManager.stopServer();
        Thread.sleep(500);
        assertFalse(serverManager.isRunning(), "Server should be stopped after second stop");
    }

    /**
     * Helper method to find the server script.
     * This mirrors the logic in PythonServerManager.
     */
    private Path findServerScript() {
        String serverScriptName = "server20a-test.py";
        Path currentDir = Paths.get(System.getProperty("user.dir"));
        
        Path[] searchPaths = {
            currentDir.resolve("../backend/src/main/PythonScripts/" + serverScriptName),
            currentDir.resolve("backend/src/main/PythonScripts/" + serverScriptName),
            currentDir.resolve("../../backend/src/main/PythonScripts/" + serverScriptName)
        };
        
        for (Path path : searchPaths) {
            try {
                Path normalized = path.normalize();
                if (Files.exists(normalized)) {
                    return normalized;
                }
            } catch (Exception e) {
                // Ignore and try next path
            }
        }
        
        return null;
    }
}
