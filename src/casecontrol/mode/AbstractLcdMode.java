package casecontrol.mode;

import java.awt.*;
import java.util.Arrays;

import casecontrol.Data;

abstract class AbstractLcdMode implements LcdMode {

  protected final String[] text = new String[Data.LCD_HEIGHT];

  public AbstractLcdMode() {
    Arrays.fill(text, "");
  }

  @Override
  public Color getColor() {
    return Data.lcdStaticColor;
  }

  @Override
  public String[] getText() {
    return text;
  }
}
