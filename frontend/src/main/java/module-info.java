module org.example.frontend {
    requires javafx.controls;
    requires javafx.fxml;
    requires backend;
    requires javafx.base;
    requires javafx.graphics;
    // java.net.http is needed by RestServerLauncher to poll /health
    requires java.net.http;
    // java.logging is needed by RestServerLauncher for Logger
    requires java.logging;


    opens org.viewScreens to javafx.fxml;
    exports org.viewScreens;
    exports org.services;
}