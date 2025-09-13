package org.example.util;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;

public class TestUtils {
    public static String readJsonFile(String filename) throws IOException {
        Path resourceDirectory = Paths.get("src", "test", "java", "resources", filename);

        if (!Files.exists(resourceDirectory)) {
            throw new IOException("File not found: " + resourceDirectory.toAbsolutePath());
        }

        return Files.readString(resourceDirectory);
    }
}