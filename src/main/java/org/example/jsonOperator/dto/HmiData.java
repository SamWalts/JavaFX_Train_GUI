package org.example.jsonOperator.dto;

import com.fasterxml.jackson.annotation.JsonProperty;

/*
Data class for HMI data. "INDEX" value will be the key used in the map.
 */
public class HmiData {

    @JsonProperty("INDEX")
    private Integer index;

    @JsonProperty("TAG")
    private String tag;

    @JsonProperty("HMI_VALUEb")
    private Boolean hmiValueb;

    @JsonProperty("HMI_VALUEi")
    private Integer hmiValuei;

    @JsonProperty("PI_VALUEf")
    private Float piValuef;

    @JsonProperty("PI_VALUEb")
    private Boolean piValueb;

    @JsonProperty("HMI_READi")
    private Integer hmiReadi;


    // Getters and setters
    public Integer getIndex() {
        return index;
    }

    public void setIndex(Integer index) {
        this.index = index;
    }

    public String getTag() {
        return tag;
    }

    public void setTag(String tag) {
        this.tag = tag;
    }

    public Boolean getHmiValueb() {
        return hmiValueb;
    }

    public void setHmiValueb(Boolean hmiValueb) {
        this.hmiValueb = hmiValueb;
    }

    public Integer getHmiValuei() {
        return hmiValuei;
    }

    public void setHmiValuei(Integer hmiValuei) {
        this.hmiValuei = hmiValuei;
    }

    public Float getPiValuef() {
        return piValuef;
    }

    public void setPiValuef(Float piValuef) {
        this.piValuef = piValuef;
    }

    public Boolean getPiValueb() {
        return piValueb;
    }

    public void setPiValueb(Boolean piValueb) {
        this.piValueb = piValueb;
    }

    public Integer getHmiReadi() {
        return hmiReadi;
    }

    public void setHmiReadi(Integer hmiReadi) {
        this.hmiReadi = hmiReadi;
    }


    @Override
    public String toString() {
        return "{" +
                "\"INDEX\": " + index +
                ", \"TAG\": \"" + tag + "\"" +
                ", \"HMI_VALUEi\": " + hmiValuei +
                ", \"HMI_VALUEb\": " + hmiValueb +
                ", \"PI_VALUEf\": " + piValuef +
                ", \"PI_VALUEb\": " + piValueb +
                ", \"HMI_READi\": " + hmiReadi +
                '}';
    }
}
