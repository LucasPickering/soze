package casecontrol.command.caseled;

import casecontrol.CaseControl;
import casecontrol.command.Command;

public final class CommandClearFade implements Command {
  @Override
  public String getName() {
    return "clearfade";
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
    return "Clear the list of fade colors.";
  }

  @Override
  public boolean execute(String[] args) {
    CaseControl.getData().caseFadeColors.clear();
    return true;
  }
}
