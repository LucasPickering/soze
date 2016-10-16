package me.lucaspickering.casecontrol.mode;

import java.awt.*;

public final class LcdModeOff extends AbstractLcdMode {

    @Override
    public Color getColor() {
        return Color.BLACK;
    }

    @Override
    public String toString() {
        return "Off";
    }
}
