package me.lucaspickering.casecontrol.command.caseled.fade;

import me.lucaspickering.casecontrol.command.AbstractCommand;

public class CommandFade extends AbstractCommand {

    public CommandFade() {
        super(new CommandFadeTiming(), new CommandFadeColor(), new CommandFadeSet());
    }

    @Override
    public String getName() {
        return "fade";
    }

    @Override
    public String getArgDesc() {
        return null;
    }

    @Override
    public String getFullDesc() {
        return "Contains sub-commands for case-related activities.";
    }
}
