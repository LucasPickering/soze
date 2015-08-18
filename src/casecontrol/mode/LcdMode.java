package casecontrol.mode;

import java.awt.Color;

public interface LcdMode {

  /**
   * Gets the color that the LCD should currently be.
   *
   * @return the desired color
   */
  Color getColor();

  /**
   * Gets the text that should currently be displayed on the LCD.
   *
   * @return a String[] of length {@link casecontrol.Data#LCD_HEIGHT}, with each String no longer
   * than {@link casecontrol.Data#LCD_WIDTH} characters long.
   */
  String[] getText();

}
