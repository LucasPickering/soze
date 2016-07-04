package me.lucaspickering.casecontrol.command.caseled.fade;

import java.awt.*;

import me.lucaspickering.casecontrol.CaseControl;
import me.lucaspickering.casecontrol.Data;
import me.lucaspickering.casecontrol.Funcs;
import me.lucaspickering.casecontrol.command.AbstractCommand;

public class CommandFadeColorAdd extends AbstractCommand {

	@Override
	public String getName() {
		return "add";
	}

	@Override
	public String getArgDesc() {
		return "<color>";
	}

	@Override
	public String getFullDesc() {
		return "Adds a color to the end of the current fade set.";
	}

	@Override
	public boolean execute(String[] args) {
		Color color;
		if (args.length >= 1 && (color = Funcs.getColor(args[0])) != null) {
			Data data = CaseControl.getData();
			data.caseFadeColors.add(color);
			System.out.printf("Case fade color (%d, %d, %d) added at position %d\n",
												color.getRed(), color.getGreen(), color.getBlue(),
												data.caseFadeColors.size() - 1);
			return true;
		}
		return false;
	}
}
