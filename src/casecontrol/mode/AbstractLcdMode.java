package casecontrol.mode;

import java.awt.Color;
import java.util.Arrays;

import casecontrol.CaseControl;
import casecontrol.Data;

abstract class AbstractLcdMode implements LcdMode {

  protected final String[] text = new String[Data.LCD_HEIGHT];

  public AbstractLcdMode() {
    Arrays.fill(text, "");
  }

  @Override
  public Color getColor() {
    return CaseControl.getData().lcdColor;
  }

  @Override
  public String[] getText() {
    return text;
  }
}
