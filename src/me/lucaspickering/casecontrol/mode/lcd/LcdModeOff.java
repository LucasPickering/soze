package me.lucaspickering.casecontrol.mode.lcd;

import java.awt.*;

public final class LcdModeOff extends AbstractLcdMode {

    @Override
    public EnumLcdMode getMode() {
        return EnumLcdMode.OFF;
    }

    @Override
    public Color getColor() {
        return Color.BLACK;
    }

    @Override
    public String toString() {
        return "Off";
    }
}
