package me.lucaspickering.casecontrol.command.caseled.fade;

import me.lucaspickering.casecontrol.CaseControl;
import me.lucaspickering.casecontrol.Data;
import me.lucaspickering.casecontrol.Funcs;
import me.lucaspickering.casecontrol.command.AbstractCommand;

public class CommandFadeTimingTrans extends AbstractCommand {

	@Override
	public String getName() {
		return "trans";
	}

	@Override
	public String getArgDesc() {
		return "<ticks>";
	}

	@Override
	public String getFullDesc() {
		return "Set the number of transition ticks for fading.";
	}

	@Override
	public boolean execute(String[] args) {
		final int ticks;
		try {
			ticks = Funcs.clamp(new Integer(args[0]), Data.MIN_FADE_TICKS, Data.MAX_FADE_TICKS);
		} catch (NumberFormatException e) {
			System.out.println("Tick value must be a number");
			return false; // Failed. Print help.
		}
		CaseControl.getData().caseFadeTicks = ticks;
		System.out.println("Transition ticks set to " + ticks);
		return true;
	}
}
