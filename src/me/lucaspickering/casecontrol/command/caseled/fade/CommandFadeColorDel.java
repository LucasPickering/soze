package me.lucaspickering.casecontrol.command.caseled.fade;

import me.lucaspickering.casecontrol.CaseControl;
import me.lucaspickering.casecontrol.Data;
import me.lucaspickering.casecontrol.command.AbstractCommand;

public class CommandFadeColorDel extends AbstractCommand {

	@Override
	public String getName() {
		return "del";
	}

	@Override
	public String getArgDesc() {
		return "<index>";
	}

	@Override
	public String getFullDesc() {
		return "Delets the color with the given index from the current fade set.";
	}

	@Override
	public boolean execute(String[] args) {
		if (args.length >= 0) {
			final int index;
			try {
				index = new Integer(args[0]);
			} catch (NumberFormatException e) {
				// Argument wasn't a number.
				System.out.println("Index value must be a number.");
				return false;
			}
			Data data = CaseControl.getData();
			if (0 <= index && index < data.caseFadeColors.size()) {
				data.caseFadeColors.remove(index);
				System.out.printf("Case fade color at %d removed\n", index);
			} else {
				System.out.println("Invalid index: " + index);
			}
			return true;
		}
		return false;
	}
}
