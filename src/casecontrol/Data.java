package casecontrol;

import java.awt.Color;
import java.util.ArrayList;
import java.util.List;

import casecontrol.mode.CaseMode;
import casecontrol.mode.CaseModeOff;
import casecontrol.mode.LcdMode;
import casecontrol.mode.LcdModeOff;

public final class Data {

  public static final int LCD_WIDTH = 20;
  public static final int LCD_HEIGHT = 4;
  public static final int LOOP_TIME = 30;
  public static final int MIN_FADE_TICKS = 10;
  public static final int MAX_FADE_TICKS = 200;

  public static CaseMode caseMode = new CaseModeOff();
  public static Color caseStaticColor = Color.BLACK;
  public static int caseFadeTicks = MIN_FADE_TICKS;
  public static final List<Color> caseFadeColors = new ArrayList<>();

  public static LcdMode lcdMode = new LcdModeOff();
  public static Color lcdColor = Color.BLACK;

}
