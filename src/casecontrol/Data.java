package casecontrol;

import java.awt.*;

import casecontrol.mode.CaseMode;
import casecontrol.mode.CaseModeOff;
import casecontrol.mode.LcdMode;
import casecontrol.mode.LcdModeOff;

public final class Data {

  public static final int LCD_WIDTH = 20;
  public static final int LCD_HEIGHT = 4;

  public static Color caseStaticColor = Color.BLACK;
  public static Color lcdStaticColor = Color.BLACK;
  public static CaseMode caseMode = new CaseModeOff();
  public static LcdMode lcdMode = new LcdModeOff();

}
