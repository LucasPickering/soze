package me.lucaspickering.casecontrol.command.caseled.fade;

import java.awt.*;
import java.util.List;
import java.util.Map;

import me.lucaspickering.casecontrol.CaseControl;
import me.lucaspickering.casecontrol.command.AbstractCommand;

public class CommandFadeSet extends AbstractCommand {

	public CommandFadeSet() {
		super(new CommandFadeSetSave(), new CommandFadeSetLoad(), new CommandFadeSetDel());
	}

	@Override
	public String getName() {
		return "set";
	}

	@Override
	public String getArgDesc() {
		return "";
	}

	@Override
	public String getFullDesc() {
		return "Contains sub-commands for fade set-related activities.";
	}

	@Override
	public boolean execute(String[] args) {
		// Print available fade sets, then return false to print help
		for (Map.Entry<String, List<Color>> entry : CaseControl.getData().savedFades.entrySet()) {
			System.out.println(entry.getKey());
			for (Color color : entry.getValue()) {
				System.out.printf("  (%d, %d, %d)\n", color.getRed(), color.getGreen(), color.getBlue());
			}
		}
		return false;
	}
}
