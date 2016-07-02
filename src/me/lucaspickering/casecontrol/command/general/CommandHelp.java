package me.lucaspickering.casecontrol.command.general;

import me.lucaspickering.casecontrol.command.Command;
import me.lucaspickering.casecontrol.command.EnumCommand;

public final class CommandHelp implements Command {

	@Override
	public String getName() {
		return "help";
	}

	@Override
	public int getArgumentAmount() {
		return 0;
	}

	@Override
	public String getArgs() {
		return "";
	}

	@Override
	public String getDesc() {
		return "Print the help dialog.";
	}

	@Override
	public boolean execute(String[] args) {
		for (EnumCommand enumCommand : EnumCommand.values()) {
			final Command command = enumCommand.command;
			System.out.printf("%s %s - %s\n", command.getName(), command.getArgs(), command.getDesc());
		}
		return true;
	}
}
