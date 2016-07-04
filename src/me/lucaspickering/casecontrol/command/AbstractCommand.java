package me.lucaspickering.casecontrol.command;

import java.util.HashMap;
import java.util.Map;

public abstract class AbstractCommand implements Command {

	private final Map<String, Command> subcommands = new HashMap<>();

	protected AbstractCommand(Command... subcomms) {
		for (Command command : subcomms) {
			subcommands.put(command.getName(), command);
		}
	}

	@Override
	public final boolean isSubcommand(String subcommand) {
		return subcommands.containsKey(subcommand);
	}

	@Override
	public final Command getSubcommand(String subcommand) {
		return subcommands.get(subcommand);
	}

	@Override
	public boolean execute(String[] args) {
		return false;
	}

	@Override
	public boolean equals(Object o) {
		if (this == o) {
			return true;
		}
		if (o == null || !(o instanceof Command)) {
			return false;
		}

		AbstractCommand other = (AbstractCommand) o;
		return getName().equals(other.getName());

	}

	@Override
	public int hashCode() {
		return getName().hashCode();
	}
}
