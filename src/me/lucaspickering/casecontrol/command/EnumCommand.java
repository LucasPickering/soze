package me.lucaspickering.casecontrol.command;

import me.lucaspickering.casecontrol.command.caseled.CommandCase;
import me.lucaspickering.casecontrol.command.caseled.fade.CommandFade;
import me.lucaspickering.casecontrol.command.general.CommandExit;
import me.lucaspickering.casecontrol.command.general.CommandHelp;
import me.lucaspickering.casecontrol.command.lcd.CommandLcd;

public enum EnumCommand {

    EXIT(CommandExit.class), HELP(CommandHelp.class),
    CASE(CommandCase.class), FADE(CommandFade.class), LCD(CommandLcd.class);

    public final Command command;

    EnumCommand(Class<? extends Command> commandClass) {
        Command command = null;
        try {
            command = commandClass.newInstance();
        } catch (IllegalAccessException | InstantiationException e) {
            e.printStackTrace();
        }
        this.command = command;
    }
}
