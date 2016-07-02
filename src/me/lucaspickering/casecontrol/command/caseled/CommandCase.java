package me.lucaspickering.casecontrol.command.caseled;

import me.lucaspickering.casecontrol.command.AbstractCommand;

public class CommandCase extends AbstractCommand {

	public CommandCase() {
		super(new CommandCaseMode(), new CommandCaseColor());
	}

	@Override
	public String getName() {
		return "case";
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
