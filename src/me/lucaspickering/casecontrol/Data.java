package me.lucaspickering.casecontrol;

import java.awt.*;
import java.io.Serializable;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

import me.lucaspickering.casecontrol.mode.EnumCaseMode;
import me.lucaspickering.casecontrol.mode.EnumLcdMode;

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

    public EnumCaseMode caseMode = EnumCaseMode.OFF;
    public Color caseStaticColor = Color.BLACK;
    public int caseFadeTicks = 50;
    public int casePauseTicks = 50;
    public final List<Color> caseFadeColors = new ArrayList<>();
    public final Map<String, List<Color>> savedFades = new HashMap<>();

    public EnumLcdMode lcdMode = EnumLcdMode.OFF;
    public Color lcdStaticColor = Color.BLACK;

    public Color caseColor = caseStaticColor;
    public Color lcdColor = lcdStaticColor;
    public String[] lcdText = new String[LCD_HEIGHT];
}
