package me.lucaspickering.casecontrol.command.general;

import me.lucaspickering.casecontrol.command.Command;

public final class CommandExit implements Command {

	@Override
	public String getName() {
		return "exit";
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
		return "Terminate the program.";
	}

	@Override
	public boolean execute(String args[]) {
		return false;
	}
}
