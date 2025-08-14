module org.example.frontend {
    requires javafx.controls;
    requires javafx.fxml;
    requires backend;


    opens org.viewScreens to javafx.fxml;
    exports org.viewScreens;
}