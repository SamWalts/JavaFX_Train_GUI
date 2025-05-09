module org.example.frontend {
    requires javafx.controls;
    requires javafx.fxml;
    requires backend;

    opens org.javafx to javafx.fxml;
    exports org.javafx;
}