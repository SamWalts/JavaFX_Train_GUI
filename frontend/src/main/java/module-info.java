module org.example.frontend {
    requires javafx.controls;
    requires javafx.fxml;
    requires backend;
    requires javafx.base;


    opens org.viewScreens to javafx.fxml;
    exports org.viewScreens;
}