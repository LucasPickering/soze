package me.lucaspickering.casecontrol.command.caseled.fade;

import java.util.LinkedList;

import me.lucaspickering.casecontrol.CaseControl;
import me.lucaspickering.casecontrol.Data;
import me.lucaspickering.casecontrol.command.AbstractCommand;

public class CommandFadeSetSave extends AbstractCommand {

	@Override
	public String getName() {
		return "save";
	}

	@Override
	public String getArgDesc() {
		return "<name>";
	}

	@Override
	public String getFullDesc() {
		return "Saves the current fade set under the given name.";
	}

	@Override
	public boolean execute(String[] args) {
		if (args.length >= 1) {
			final Data data = CaseControl.getData();
			if (data.caseFadeColors.isEmpty()) {
				System.out.println("Fade list is empty, nothing saved");
			} else if (args.length == 0) {
				return false;
			} else {
				final String name = args[0];
				data.savedFades.put(name, new LinkedList<>(data.caseFadeColors));
				System.out.println("Saved current fade set under " + name);
			}
			return true;
		}
		return false;
	}
}
