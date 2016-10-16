package me.lucaspickering.casecontrol.command.caseled.fade;

import me.lucaspickering.casecontrol.CaseControl;
import me.lucaspickering.casecontrol.command.AbstractCommand;

public class CommandFadeColorClear extends AbstractCommand {

    @Override
    public String getName() {
        return "clear";
    }

    @Override
    public String getArgDesc() {
        return null;
    }

    @Override
    public String getFullDesc() {
        return "Clears all the colors from the current fade set.";
    }

    @Override
    public boolean execute(String[] args) {
        CaseControl.getData().caseFadeColors.clear();
        return true;
    }
}
