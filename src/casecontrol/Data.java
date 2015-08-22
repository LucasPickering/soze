package casecontrol;

import java.awt.Color;
import java.io.Serializable;
import java.util.ArrayList;
import java.util.List;

import casecontrol.mode.CaseMode;
import casecontrol.mode.CaseModeOff;
import casecontrol.mode.LcdMode;
import casecontrol.mode.LcdModeOff;

public final class Data implements Serializable {

  public static final int LCD_WIDTH = 20;
  public static final int LCD_HEIGHT = 4;
  public static final int LOOP_TIME = 30;
  public static final int MIN_FADE_TICKS = 10;
  public static final int MAX_FADE_TICKS = 200;
  public static final String DATA_FILE = "data.ser";

  public CaseMode caseMode = new CaseModeOff();
  public Color caseStaticColor = Color.BLACK;
  public int caseFadeTicks = MIN_FADE_TICKS;
  public final List<Color> caseFadeColors = new ArrayList<>();

  public LcdMode lcdMode = new LcdModeOff();
  public Color lcdColor = Color.BLACK;

}
