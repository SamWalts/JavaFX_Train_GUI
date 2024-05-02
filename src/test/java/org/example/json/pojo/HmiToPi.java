package org.example.json.pojo;

import com.fasterxml.jackson.annotation.JsonProperty;

public class HmiToPi {
    private String tag;
    private int hmiValuei;
    private boolean hmiValueb;
    private double piValuef;
    private Boolean piValueb;
    private int hmiReadi;

    // Getters and setters
    @JsonProperty("TAG")
    public String getTag() {
        return tag;
    }

    public void setTag(String tag) {
        this.tag = tag;
    }

    @JsonProperty("HMI_VALUEi")
    public int getHmiValuei() {
        return hmiValuei;
    }

    public void setHmiValuei(int hmiValuei) {
        this.hmiValuei = hmiValuei;
    }

    @JsonProperty("HMI_VALUEb")
    public boolean isHmiValueb() {
        return hmiValueb;
    }

    public void setHmiValueb(boolean hmiValueb) {
        this.hmiValueb = hmiValueb;
    }

    @JsonProperty("PI_VALUEf")
    public double getPiValuef() {
        return piValuef;
    }

    public void setPiValuef(double piValuef) {
        this.piValuef = piValuef;
    }

    @JsonProperty("PI_VALUEb")
    public Boolean getPiValueb() {
        return piValueb;
    }

    public void setPiValueb(Boolean piValueb) {
        this.piValueb = piValueb;
    }

    @JsonProperty("HMI_READi")
    public int getHmiReadi() {
        return hmiReadi;
    }

    public void setHmiReadi(int hmiReadi) {
        this.hmiReadi = hmiReadi;
    }



}
