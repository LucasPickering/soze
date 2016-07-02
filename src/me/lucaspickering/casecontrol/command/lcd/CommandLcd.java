package me.lucaspickering.casecontrol.command.lcd;

import me.lucaspickering.casecontrol.command.AbstractCommand;

public class CommandLcd extends AbstractCommand {

	public CommandLcd() {
		super(new CommandLcdMode(), new CommandLcdColor());
	}

	@Override
	public String getName() {
		return "lcd";
	}

	@Override
	public String getArgDesc() {
		return "";
	}

	@Override
	public String getFullDesc() {
		return "Contains sub-commands for LCD-related activities.";
	}
}
