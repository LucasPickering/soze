package me.lucaspickering.casecontrol.command.general;

import me.lucaspickering.casecontrol.Funcs;
import me.lucaspickering.casecontrol.command.AbstractCommand;
import me.lucaspickering.casecontrol.command.EnumCommand;

public final class CommandHelp extends AbstractCommand {

    @Override
    public String getName() {
        return "help";
    }

    @Override
    public String getArgDesc() {
        return null;
    }

    @Override
    public String getFullDesc() {
        return "Prints help for each command.";
    }

    @Override
    public boolean execute(String[] args) {
        for (EnumCommand enumCommand : EnumCommand.values()) {
            Funcs.printCommandInfo(enumCommand.command);
        }
        return true;
    }
}
