module org.example.frontend {
    requires javafx.controls;
    requires javafx.fxml;
    requires backend;
    requires javafx.base;
    requires java.logging;


    opens org.viewScreens to javafx.fxml;
    exports org.viewScreens;
}