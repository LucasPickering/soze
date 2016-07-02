package me.lucaspickering.casecontrol.command.general;

import me.lucaspickering.casecontrol.command.AbstractCommand;
import me.lucaspickering.casecontrol.command.Command;
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
			final Command command = enumCommand.command;
			final String name = command.getName();
			final String argDesc = command.getArgDesc();
			final String fullDesc = command.getFullDesc();

			// Print info for each command
			if (argDesc == null) {
				System.out.printf("%s - %s\n", name, fullDesc);
			} else {
				System.out.printf("%s %s - %s\n", name, argDesc, fullDesc);
			}
		}
		return true;
	}
}
