package me.lucaspickering.casecontrol.mode.lcd;

import java.awt.Color;

import me.lucaspickering.casecontrol.CaseControl;

abstract class AbstractLcdMode implements LcdMode {

    private final EnumLcdMode lcdMode;

    AbstractLcdMode(EnumLcdMode lcdMode) {
        this.lcdMode = lcdMode;
    }

    @Override
    public final EnumLcdMode getMode() {
        return lcdMode;
    }

    @Override
    public Color getColor() {
        return CaseControl.data().getLcdStaticColor();
    }

    @Override
    public String toString() {
        return lcdMode.name;
    }
}
