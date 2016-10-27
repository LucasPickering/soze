package me.lucaspickering.casecontrol.mode.caseled;

import java.awt.Color;

public final class CaseModeOff extends AbstractCaseMode {

    public CaseModeOff() {
        super(EnumCaseMode.OFF);
    }

    @Override
    public Color getColor() {
        return Color.BLACK;
    }
}
