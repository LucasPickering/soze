package me.lucaspickering.casecontrol.command.caseled;

import java.awt.*;

import me.lucaspickering.casecontrol.CaseControl;
import me.lucaspickering.casecontrol.Data;
import me.lucaspickering.casecontrol.Funcs;
import me.lucaspickering.casecontrol.command.AbstractCommand;
import me.lucaspickering.casecontrol.mode.caseled.EnumCaseMode;

public class CommandCaseColor extends AbstractCommand {

    @Override
    public String getName() {
        return "color";
    }

    @Override
    public String getArgDesc() {
        return "<color>";
    }

    @Override
    public String getFullDesc() {
        return "Set the current color of the case. Also switches to static mode.";
    }

    @Override
    public boolean execute(String[] args) {
        Color color;
        if (args.length >= 1 && (color = Funcs.getColor(args)) != null) {
            Data data = CaseControl.data();
            data.caseStaticColor = color; // Set the static color
            data.caseMode = EnumCaseMode.STATIC; // Set the mode to static
            return true;
        } else {
            return false;
        }
    }
}
