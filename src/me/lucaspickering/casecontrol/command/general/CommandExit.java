package me.lucaspickering.casecontrol.command.general;

import me.lucaspickering.casecontrol.CaseControl;
import me.lucaspickering.casecontrol.command.AbstractCommand;

public final class CommandExit extends AbstractCommand {

    @Override
    public String getName() {
        return "exit";
    }

    @Override
    public String getArgDesc() {
        return null;
    }

    @Override
    public String getFullDesc() {
        return "Stops the program.";
    }

    @Override
    public boolean execute(String args[]) {
        CaseControl.stop();
        return true;
    }
}
