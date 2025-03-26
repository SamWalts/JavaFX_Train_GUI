module org.javafx {
    requires javafx.controls;
    requires javafx.fxml;

    opens org.javafx to javafx.fxml;
    exports org.javafx;
}
