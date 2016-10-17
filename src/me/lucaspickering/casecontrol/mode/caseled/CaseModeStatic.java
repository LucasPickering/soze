package me.lucaspickering.casecontrol.mode.caseled;

import java.awt.*;

import me.lucaspickering.casecontrol.CaseControl;

public final class CaseModeStatic implements CaseMode {

    @Override
    public EnumCaseMode getMode() {
        return EnumCaseMode.STATIC;
    }

    @Override
    public Color getColor() {
        return CaseControl.getData().caseStaticColor;
    }

    @Override
    public String toString() {
        return "Static";
    }
}
