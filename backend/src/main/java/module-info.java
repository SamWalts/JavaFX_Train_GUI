module backend {
    requires com.fasterxml.jackson.annotation;
    requires com.fasterxml.jackson.databind;
    requires java.logging;

    exports org.example.jsonOperator.dto;
    exports org.example.jsonOperator.dao;
    exports org.example.Client;

}