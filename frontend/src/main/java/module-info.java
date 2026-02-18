module org.example.frontend {
    requires javafx.controls;
    requires javafx.fxml;
    requires backend;
    requires javafx.base;
    requires javafx.graphics;


    opens org.viewScreens to javafx.fxml;
    exports org.viewScreens;
    exports org.services;
}