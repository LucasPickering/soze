package me.lucaspickering.casecontrol.mode.lcd;

import java.awt.Color;
import java.util.Arrays;

import me.lucaspickering.casecontrol.CaseControl;
import me.lucaspickering.casecontrol.Consts;

abstract class AbstractLcdMode implements LcdMode {

    protected final String[] text = new String[Consts.LCD_HEIGHT];

    public AbstractLcdMode() {
        Arrays.fill(text, "");
    }

    @Override
    public Color getColor() {
        return CaseControl.data().getLcdStaticColor();
    }

    @Override
    public String[] getText() {
        return text;
    }
}