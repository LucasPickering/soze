package me.lucaspickering.casecontrol.command.general;

import me.lucaspickering.casecontrol.CaseControl;
import me.lucaspickering.casecontrol.Data;
import me.lucaspickering.casecontrol.command.Command;

public final class CommandInfo implements Command {

	@Override
	public String getName() {
		return "info";
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
		return "Print the current settings.";
	}

	@Override
	public boolean execute(String[] args) {
		final Data data = CaseControl.getData();
		System.out.println("---Case---");
		System.out.printf("Mode: %s\n", data.caseMode);
		System.out.printf("Fade ticks: %d\n", data.caseFadeTicks);
		System.out.printf("Pause ticks: %d\n", data.casePauseTicks);

		System.out.println("\n---LCD---");
		System.out.printf("Mode: %s\n", data.lcdMode);
		System.out.printf("Color: %s\n", data.lcdColor);
		return true;
	}
}
