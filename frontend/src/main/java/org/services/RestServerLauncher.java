package org.services;

import java.io.IOException;
import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.time.Duration;
import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.TimeUnit;
import java.util.logging.Level;
import java.util.logging.Logger;

/**
 * RestServerLauncher — starts and stops the bundled Python REST server process.
 *
 * <h2>Why this class exists</h2>
 * <p>The app is packaged with a frozen copy of {@code rest_server.py} (built by
 * PyInstaller). When a user opens the installed app there is no Python on their
 * machine — Java must start the binary itself. This class:</p>
 * <ol>
 *   <li>Finds the {@code rest_server} executable (frozen binary, venv .py script,
 *       or system PATH — in that order).</li>
 *   <li>Launches it via {@link ProcessBuilder}.</li>
 *   <li>Polls {@code /health} until the server is ready before handing control
 *       back to {@link org.viewScreens.App}.</li>
 *   <li>Shuts the process down cleanly when the JavaFX app closes.</li>
 * </ol>
 *
 * <h2>Dev-mode note</h2>
 * <p>In development (running via {@code mvn javafx:run}) there is no frozen binary.
 * The launcher falls back to running {@code rest_server.py} directly using the
 * {@code .venv/bin/python3} found next to the script, or system {@code python3}
 * if no venv is present.</p>
 *
 * <h2>How to use</h2>
 * <pre>{@code
 * RestServerLauncher launcher = new RestServerLauncher();
 * launcher.start();
 * boolean ready = launcher.awaitHealthy(20);
 * if (!ready) { // show error dialog }
 * // ... run app ...
 * launcher.stop();   // called from App.stop()
 * }</pre>
 */
public class RestServerLauncher {

    private static final Logger logger = Logger.getLogger(RestServerLauncher.class.getName());

    private static final String HEALTH_URL = "http://127.0.0.1:5000/health";
    private static final int POLL_INTERVAL_MS = 200;

    // The running server process — null if not started yet
    private Process serverProcess = null;

    // Short connect timeout so failed health checks fail fast
    private final HttpClient httpClient = HttpClient.newBuilder()
            .connectTimeout(Duration.ofSeconds(2))
            .build();

    // -----------------------------------------------------------------------
    // Public API
    // -----------------------------------------------------------------------

    /**
     * Finds and starts the REST server.
     *
     * <p>Lookup order for the server:</p>
     * <ol>
     *   <li>System property {@code traincontrol.server.binary} — set by jpackage.</li>
     *   <li>PyInstaller frozen binary at the dev path
     *       {@code backend/src/main/PythonScripts/dist/rest_server/rest_server}.</li>
     *   <li>Raw {@code rest_server.py} script — launched via the venv
     *       {@code .venv/bin/python3} if present, otherwise system {@code python3}.</li>
     * </ol>
     *
     * @throws IOException if the process fails to start
     */
    public void start() throws IOException {
        logger.info("RestServerLauncher working directory: " + Paths.get("").toAbsolutePath());

        Path binary = resolveBinary();
        if (binary == null) {
            logger.warning("rest_server binary/script not found — skipping auto-start. " +
                    "Start the server manually: cd backend/src/main/PythonScripts && python3 rest_server.py");
            return;
        }

        // Ensure ~/.traincontrol/ exists for the DB file
        Path dbPath = Path.of(System.getProperty("user.home"), ".traincontrol", "rest_server.db.json");
        Files.createDirectories(dbPath.getParent());

        List<String> command = buildCommand(binary, dbPath);
        logger.log(Level.INFO, "Starting REST server: {0}", String.join(" ", command));

        ProcessBuilder pb = new ProcessBuilder(command);
        pb.inheritIO(); // server stdout/stderr appears in our console
        serverProcess = pb.start();

        logger.info("REST server process started (PID: " + serverProcess.pid() + ")");
    }

    /**
     * Polls {@code /health} every 500 ms until the server responds with HTTP 200
     * or the timeout expires.
     *
     * <p>Think of this as knocking on a door repeatedly until someone answers.</p>
     *
     * @param timeoutSeconds how many seconds to wait before giving up
     * @return {@code true} if the server became healthy in time
     */
    public boolean awaitHealthy(int timeoutSeconds) {
        long deadline = System.currentTimeMillis() + (long) timeoutSeconds * 1000;
        int attempts = 0;

        try { Thread.sleep(2000);} catch (InterruptedException e) { Thread.currentThread().interrupt(); return false; } // give server a moment to start
        logger.info("Waiting for REST server to become healthy (timeout: " + timeoutSeconds + "s)...");

        while (System.currentTimeMillis() < deadline) {
            attempts++;
            if (isHealthy()) {
                logger.info("REST server is healthy after " + attempts + " attempt(s)");
                return true;
            }
            try {
                Thread.sleep(POLL_INTERVAL_MS);
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
                return false;
            }
        }

        logger.warning("REST server did not become healthy within " + timeoutSeconds + "s (" + attempts + " attempts)");
        return false;
    }

    /**
     * Stops the REST server process gracefully, then forcibly if it doesn't exit
     * within 3 seconds. Called from {@link org.viewScreens.App#stop()}.
     */
    public void stop() {
        if (serverProcess == null || !serverProcess.isAlive()) {
            logger.fine("REST server process is not running — nothing to stop");
            return;
        }

        logger.info("Stopping REST server (PID: " + serverProcess.pid() + ")...");
        serverProcess.destroy(); // polite SIGTERM

        try {
            boolean exited = serverProcess.waitFor(3, TimeUnit.SECONDS);
            if (!exited) {
                logger.warning("REST server did not exit in 3s — force-killing");
                serverProcess.destroyForcibly(); // SIGKILL
            }
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
            serverProcess.destroyForcibly();
        }

        logger.info("REST server stopped");
        serverProcess = null;
    }

    // -----------------------------------------------------------------------
    // Private helpers
    // -----------------------------------------------------------------------

    /**
     * Resolves the path to either the frozen binary or the {@code .py} script.
     * Returns {@code null} if neither can be found.
     *
     * <p>Paths are tried relative to every candidate root directory so the app
     * works whether it is launched from the project root, from the
     * {@code frontend/} subdirectory (IntelliJ default), or as an installed
     * jpackage bundle.</p>
     */
    private Path resolveBinary() {
        // 1 — jpackage sets this system property via --java-options
        String sysProp = System.getProperty("traincontrol.server.binary");
        if (sysProp != null) {
            Path p = Paths.get(sysProp);
            if (Files.isExecutable(p)) {
                logger.info("Found rest_server from system property: " + p);
                return p;
            }
            logger.warning("traincontrol.server.binary points to non-executable path: " + p);
        }

        // 2 — Installed app bundle: search relative to the running JVM.
        // jpackage places app content next to the JVM runtime inside the bundle.
        // macOS: TrainControl.app/Contents/runtime/  → app content is in Contents/
        // Windows/Linux: app/runtime/                → app content is in app/
        // With --onefile the binary is a single file: Contents/rest_server (macOS)
        try {
            Path check = Paths.get(System.getProperty("java.home")).toAbsolutePath();
            for (int i = 0; i < 3; i++) {
                check = check.getParent();
                if (check == null) break;
                // --onefile: single binary directly inside the bundle content dir
                Path candidate = check.resolve("rest_server");
                if (Files.isExecutable(candidate) && !Files.isDirectory(candidate)) {
                    logger.info("Found rest_server relative to java.home: " + candidate);
                    return candidate;
                }
                Path candidateExe = check.resolve("rest_server.exe");
                if (Files.isExecutable(candidateExe)) {
                    logger.info("Found rest_server.exe relative to java.home: " + candidateExe);
                    return candidateExe;
                }
            }
        } catch (Exception e) {
            logger.warning("Error searching relative to java.home: " + e.getMessage());
        }

        // 3 — Dev mode: PyInstaller frozen binary (--onefile: single file in dist/)
        // cwd may be project root or frontend/ depending on how IntelliJ launches
        Path cwd = Paths.get("").toAbsolutePath();
        Path[] roots = { cwd, cwd.getParent() };
        String[] frozenRelative = {
                "backend/src/main/PythonScripts/dist/rest_server",
                "backend/src/main/PythonScripts/dist/rest_server.exe",
        };
        for (Path root : roots) {
            if (root == null) continue;
            for (String rel : frozenRelative) {
                Path p = root.resolve(rel);
                if (Files.isExecutable(p)) {
                    logger.info("Found frozen rest_server at: " + p);
                    return p;
                }
            }
        }

        // 4 — Dev mode: raw .py script (launched via python3 in buildCommand)
        for (Path root : roots) {
            if (root == null) continue;
            Path script = root.resolve("backend/src/main/PythonScripts/rest_server.py");
            if (Files.exists(script)) {
                logger.info("Found rest_server.py script at: " + script);
                return script;
            }
        }

        logger.warning("rest_server binary and script not found under: " + cwd);
        return null;
    }

    /**
     * Builds the OS command to run based on whether {@code binary} is a frozen
     * executable or a {@code .py} script.
     *
     * <ul>
     *   <li><b>Frozen binary</b> — run it directly.</li>
     *   <li><b>.py script</b> — prefix with {@code .venv/bin/python3} if a venv
     *       exists next to the script, otherwise fall back to system
     *       {@code python3}.</li>
     * </ul>
     */
    private List<String> buildCommand(Path binary, Path dbPath) {
        List<String> command = new ArrayList<>();

        if (binary.toString().endsWith(".py")) {
            // Dev mode — use the venv python3 if it exists, else system python3
            Path venvPython = binary.getParent().resolve(".venv/bin/python3");
            if (Files.isExecutable(venvPython)) {
                logger.info("Using venv python3: " + venvPython);
                command.add(venvPython.toAbsolutePath().toString());
            } else {
                logger.info("venv not found — using system python3");
                command.add("python3");
            }
            command.add(binary.toAbsolutePath().toString());
        } else {
            // Frozen binary — run directly
            command.add(binary.toAbsolutePath().toString());
        }

        command.add("--db-path");
        command.add(dbPath.toAbsolutePath().toString());
        return command;
    }

    /**
     * Makes a single GET request to {@code /health}.
     * Returns {@code true} if the server responds with HTTP 200.
     */
    private boolean isHealthy() {
        try {
            HttpRequest req = HttpRequest.newBuilder()
                    .uri(URI.create(HEALTH_URL))
                    .GET()
                    .build();
            HttpResponse<Void> resp = httpClient.send(req, HttpResponse.BodyHandlers.discarding());
            return resp.statusCode() == 200;
        } catch (Exception e) {
            // Connection refused / timeout — server not ready yet, not an error
            logger.fine("Health check not ready yet: " + e.getMessage());
            return false;
        }
    }
}
