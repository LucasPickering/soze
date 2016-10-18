package me.lucaspickering.casecontrol.mode.lcd;

import java.awt.Color;

import me.lucaspickering.casecontrol.CaseControl;

abstract class AbstractLcdMode implements LcdMode {

    @Override
    public Color getColor() {
        return CaseControl.data().getLcdStaticColor();
    }

}
