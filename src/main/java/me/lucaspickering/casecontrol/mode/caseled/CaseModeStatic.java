package me.lucaspickering.casecontrol.mode.caseled;

import java.awt.*;

import me.lucaspickering.casecontrol.CaseControl;

public final class CaseModeStatic extends AbstractCaseMode {

    public CaseModeStatic() {
        super(EnumCaseMode.STATIC);
    }

    @Override
    public Color getColor() {
        return CaseControl.data().getCaseStaticColor();
    }
}
