package org.example.jsonOperator.service;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.*;
import org.example.jsonOperator.dao.IHMIJSONDAO;
import org.example.jsonOperator.dto.HmiData;

import java.io.File;
import java.io.IOException;
import java.util.*;

public class JSONOperatorServiceStub implements IJSONOperatorService {
    private static final ObjectMapper objectMapper = getDefaultObjectMapper();
    private final IHMIJSONDAO<HmiData> hmiJsonDao;

    public JSONOperatorServiceStub(IHMIJSONDAO<HmiData> hmiJsonDao) {
        this.hmiJsonDao = hmiJsonDao;
    }

    private static ObjectMapper getDefaultObjectMapper() {
        ObjectMapper defaultObjectMapper = new ObjectMapper();
        defaultObjectMapper.configure(DeserializationFeature.FAIL_ON_UNKNOWN_PROPERTIES, false);
        return defaultObjectMapper;
    }

    private static String generateString(JsonNode node, boolean pretty) throws JsonProcessingException {
        ObjectWriter objectWriter = objectMapper.writer();
        if (pretty)
            objectWriter = objectWriter.with(SerializationFeature.INDENT_OUTPUT);
        return objectWriter.writeValueAsString(node);
    }

    @Override
    public Map<String, HmiData> readHmiDataMapFromFile(String filePath) throws IOException {
        Map<String, HmiData> hmiDataMap = objectMapper.readValue(new File(filePath), new TypeReference<>() {});
        hmiJsonDao.setHmiDataMap(hmiDataMap);
        updateIndexWithKeyValue(hmiDataMap);
        return hmiDataMap;
    }

    private void updateIndexWithKeyValue(Map<String, HmiData> hmiDataMap) {
        Map<String, HmiData> updatedIndexMap = new HashMap<>();

        for (Map.Entry<String, HmiData> entry : hmiDataMap.entrySet()) {
            String key = entry.getKey();
            HmiData value = entry.getValue();
            value.setIndex(Integer.parseInt(key)); // Assuming the key is a string representation of the index
            updatedIndexMap.put(key, value);
        }
    }

    @Override
    public void updateValue(HmiData data, String variableName, Object newValue) {
        if (variableName.equals("HMI_READi")) {
            data.setHmiReadi(1);
        }
        switch (variableName) {
            case "HMI_VALUEi":
                data.setHmiValuei((Integer) newValue);
                data.setHmiReadi(1);
                break;
            case "HMI_VALUEb":
                data.setHmiValueb((Boolean) newValue);
                data.setHmiReadi(1);
                break;
            case "PI_VALUEf":
                data.setPiValuef((Float) newValue);
                data.setHmiReadi(1);
                break;
            case "PI_VALUEb":
                data.setPiValueb((Boolean) newValue);
                data.setHmiReadi(1);
                break;
            default:
                throw new IllegalArgumentException("Unknown variable name: " + variableName);
        }
    }

    @Override
    public void compareAndSetHMI_READi(Map<String, HmiData> hmiDataMap, Map<String, HmiData> workMap) {
        for (Map.Entry<String, HmiData> entry : hmiDataMap.entrySet()) {
            HmiData data = entry.getValue();
            HmiData originalData = workMap.get(entry.getKey());
            if (originalData != null && !data.getHmiReadi().equals(originalData.getHmiReadi())) {
                data.setHmiReadi(0);
                System.out.println("HMI_READi updated to 0 for " + data.getTag());
            }
        }
    }

    @Override
    public Map<String, HmiData> writeStringToMap(String jsonString) throws IOException {
        JsonNode jsonNode = objectMapper.readTree(jsonString);
        Map<String, HmiData> resultsMap = new HashMap<>();
        Iterator<JsonNode> elements = jsonNode.elements();
        while (elements.hasNext()) {
            JsonNode element = elements.next();
            if (element.has("INDEX")) {
                String index = element.get("INDEX").asText();
                HmiData hmiData = objectMapper.treeToValue(element, HmiData.class);
                hmiData.setIndex(Integer.parseInt(index)); // Keep the INDEX value in HmiData
                resultsMap.put(index, hmiData);
            } else {
                System.err.println("Missing INDEX field in element: " + element);
            }
        }
        hmiJsonDao.setHmiDataMap(resultsMap);
        return resultsMap;
    }

    @Override
    public void writeMapToFile(Map<String, ?> map, String filePath) throws IOException {
        objectMapper.configure(SerializationFeature.INDENT_OUTPUT, true);
        objectMapper.writeValue(new File(filePath), map);
    }

    @Override
    public String writeMapToString(Map<String, HmiData> map) throws JsonProcessingException {
        Map<String, HmiData> sortedMap = new TreeMap<>(Comparator.comparingInt(Integer::parseInt));
        sortedMap.putAll(map);
        System.out.println(sortedMap.values());
        return objectMapper.writeValueAsString(sortedMap.values());
    }

    @Override
    public void printMap(Map<String, HmiData> map) {
        System.out.println(hmiJsonDao.fetchAll());
    }
}