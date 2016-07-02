package me.lucaspickering.casecontrol.command.caseled.fade;

import me.lucaspickering.casecontrol.command.AbstractCommand;

public class CommandFadeTiming extends AbstractCommand {

  public CommandFadeTiming() {
    super(new CommandFadeTimingTrans(), new CommandFadeTimingPause());
  }

  @Override
  public String getName() {
    return "timing";
  }

  @Override
  public String getArgDesc() {
    return "";
  }

  @Override
  public String getFullDesc() {
    return "Contains sub-commands for fade timing-related activities.";
  }

  @Override
  public boolean execute(String[] args) {
    // Print current fade timing settings, then return false to print help
    // TODO: Print fade timings
    return false;
  }
}
