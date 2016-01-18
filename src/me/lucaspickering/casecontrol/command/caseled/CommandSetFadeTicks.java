package me.lucaspickering.casecontrol.command.caseled;

import me.lucaspickering.casecontrol.CaseControl;
import me.lucaspickering.casecontrol.Data;
import me.lucaspickering.casecontrol.Funcs;
import me.lucaspickering.casecontrol.command.Command;

public final class CommandSetFadeTicks implements Command {
  @Override
  public String getName() {
    return "fadeticks";
  }

  @Override
  public int getArgumentAmount() {
    return 1;
  }

  @Override
  public String getArgs() {
    return "<ticks>";
  }

  @Override
  public String getDesc() {
    return "Set the amount of ticks it takes to fade between colors.";
  }

  @Override
  public boolean execute(String[] args) {
    final int ticks;
    try {
      ticks = Funcs.clamp(new Integer(args[0]), Data.MIN_FADE_TICKS, Data.MAX_FADE_TICKS);
    } catch (NumberFormatException e) {
      System.out.println("Tick value must be a number");
      return true;
    }
    CaseControl.getData().caseFadeTicks = ticks;
    System.out.println("Fade ticks set to " + ticks);
    return true;
  }
}
