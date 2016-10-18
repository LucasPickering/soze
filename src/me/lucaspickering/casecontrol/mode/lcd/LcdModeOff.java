package me.lucaspickering.casecontrol.mode.lcd;

import java.awt.Color;
import java.util.Arrays;

import me.lucaspickering.casecontrol.Consts;

public final class LcdModeOff extends AbstractLcdMode {

    private static final String[] BLANK_SCREEN = new String[Consts.LCD_HEIGHT];

    static {
        Arrays.fill(BLANK_SCREEN, ""); // Fill it with empty strings
    }

    @Override
    public EnumLcdMode getMode() {
        return EnumLcdMode.OFF;
    }

    @Override
    public Color getColor() {
        return Color.BLACK;
    }

    @Override
    public String[] getText() {
        return BLANK_SCREEN;
    }
}
