package me.lucaspickering.casecontrol.mode;

import java.awt.*;

public final class CaseModeOff implements CaseMode {

    @Override
    public Color getColor() {
        return Color.BLACK;
    }

    @Override
    public String toString() {
        return "Off";
    }
}
