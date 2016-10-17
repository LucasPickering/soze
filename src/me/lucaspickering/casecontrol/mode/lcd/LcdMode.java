package me.lucaspickering.casecontrol.mode.lcd;

import java.awt.*;

public interface LcdMode {

    /**
     * Gets the {@link EnumLcdMode} for this mode.
     *
     * @return the appropriate {@link EnumLcdMode}
     */
    EnumLcdMode getMode();

    /**
     * Gets the color that the LCD should currently be.
     *
     * @return the desired color
     */
    Color getColor();

    /**
     * Gets the text that should currently be displayed on the LCD.
     *
     * @return a String[] of length {@link me.lucaspickering.casecontrol.Data#LCD_HEIGHT}, with each
     * String no longer than {@link me.lucaspickering.casecontrol.Data#LCD_WIDTH} characters long.
     */
    String[] getText();

}
