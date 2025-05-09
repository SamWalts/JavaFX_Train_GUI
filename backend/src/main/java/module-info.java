module backend {
    requires com.fasterxml.jackson.annotation;
    requires com.fasterxml.jackson.databind;

    exports org.example.jsonOperator.dto;
    exports org.example.jsonOperator.dao;
}