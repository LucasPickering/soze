package me.lucaspickering.casecontrol;

import java.awt.*;
import java.io.Serializable;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

import me.lucaspickering.casecontrol.mode.caseled.EnumCaseMode;
import me.lucaspickering.casecontrol.mode.lcd.EnumLcdMode;

public final class Data implements Serializable {

    public static final int LCD_WIDTH = 20;
    public static final int LCD_HEIGHT = 4;
    public static final int MODE_LOOP_TIME = 30;
    public static final int MIN_FADE_TICKS = 10;
    public static final int MAX_FADE_TICKS = 200;
    public static final int MIN_PAUSE_TICKS = 0;
    public static final int MAX_PAUSE_TICKS = 200;
    public static final String DATA_FILE = "data.ser";
    public static final String TEMPS_FILE = "C:/Program Files (x86)/SpeedFan/SFLog%s.csv";

    // Case parameters
    private EnumCaseMode caseMode = EnumCaseMode.OFF;
    private Color caseStaticColor = Color.BLACK;
    private int caseFadeTicks = 50;
    private int casePauseTicks = 50;
    private final List<Color> caseFadeColors = new ArrayList<>();
    private final Map<String, List<Color>> savedFades = new HashMap<>();

    // LCD parameters
    private EnumLcdMode lcdMode = EnumLcdMode.OFF;
    private Color lcdStaticColor = Color.BLACK;

    // Actual values sent to the Arduino
    private Color caseColor = caseStaticColor;
    private Color lcdColor = lcdStaticColor;
    private String[] lcdText = new String[LCD_HEIGHT];

    public EnumCaseMode getCaseMode() {
        return caseMode;
    }

    public void setCaseMode(EnumCaseMode caseMode) {
        this.caseMode = caseMode;
    }

    public Color getCaseStaticColor() {
        return caseStaticColor;
    }

    public void setCaseStaticColor(Color caseStaticColor) {
        this.caseStaticColor = caseStaticColor;
    }

    public int getCaseFadeTicks() {
        return caseFadeTicks;
    }

    /**
     * Sets the case fade time, in ticks. Clamps the value to a valid range.
     *
     * @param caseFadeTicks the desired value
     * @return the clamped value
     */
    public int setCaseFadeTicks(int caseFadeTicks) {
        return this.caseFadeTicks = Funcs.clamp(caseFadeTicks, MIN_FADE_TICKS, MAX_FADE_TICKS);
    }

    public int getCasePauseTicks() {
        return casePauseTicks;
    }

    /**
     * Sets the case pause time, in ticks. Clamps the value to a valid range.
     *
     * @param casePauseTicks the desired value
     * @return the clamped value
     */
    public int setCasePauseTicks(int casePauseTicks) {
        return this.casePauseTicks = Funcs.clamp(casePauseTicks, MIN_PAUSE_TICKS, MAX_PAUSE_TICKS);
    }

    public List<Color> getCaseFadeColors() {
        return caseFadeColors;
    }

    public Map<String, List<Color>> getSavedFades() {
        return savedFades;
    }

    public EnumLcdMode getLcdMode() {
        return lcdMode;
    }

    public void setLcdMode(EnumLcdMode lcdMode) {
        this.lcdMode = lcdMode;
    }

    public Color getLcdStaticColor() {
        return lcdStaticColor;
    }

    public void setLcdStaticColor(Color lcdStaticColor) {
        this.lcdStaticColor = lcdStaticColor;
    }

    public Color getCaseColor() {
        return caseColor;
    }

    public void setCaseColor(Color caseColor) {
        this.caseColor = caseColor;
    }

    public Color getLcdColor() {
        return lcdColor;
    }

    public void setLcdColor(Color lcdColor) {
        this.lcdColor = lcdColor;
    }

    public String[] getLcdText() {
        return lcdText;
    }

    public void setLcdText(String[] lcdText) {
        this.lcdText = lcdText;
    }
}
