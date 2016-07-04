package me.lucaspickering.casecontrol.command.caseled.fade;

import java.awt.*;

import me.lucaspickering.casecontrol.CaseControl;
import me.lucaspickering.casecontrol.Data;
import me.lucaspickering.casecontrol.command.AbstractCommand;

public class CommandFadeColor extends AbstractCommand {

	public CommandFadeColor() {
		super(new CommandFadeColorAdd(), new CommandFadeColorDel(), new CommandFadeColorClear());
	}

	@Override
	public String getName() {
		return "color";
	}

	@Override
	public String getArgDesc() {
		return null;
	}

	@Override
	public String getFullDesc() {
		return "Contains sub-commands for fade color-related activities.";
	}

	@Override
	public boolean execute(String[] args) {
		// Print current fade colors, then return false to print help
		Data data = CaseControl.getData();
		System.out.println("Current fade colors:");
		int i = 0;
		for (Color color : data.caseFadeColors) {
			System.out.printf("  %d - (%d, %d, %d)\n", i,
												color.getRed(), color.getGreen(), color.getBlue());
			i++;
		}
		return false;
	}
}
