package casecontrol.command;

import casecontrol.Data;
import casecontrol.mode.CaseModeFade;
import casecontrol.mode.CaseModeOff;
import casecontrol.mode.CaseModeStatic;

public final class CommandCaseMode implements Command {
  @Override
  public String getName() {
    return "casemode";
  }

  @Override
  public int getArgumentAmount() {
    return 1;
  }

  @Override
  public String getArgs() {
    return "<mode>";
  }

  @Override
  public String getDesc() {
    return "Set the mode for the case LEDs";
  }

  @Override
  public boolean execute(String[] args) {
    switch (args[0]) {
      case "off":
        Data.caseMode = new CaseModeOff();
        break;
      case "static":
        Data.caseMode = new CaseModeStatic();
        break;
      case "fade":
        Data.caseMode = new CaseModeFade();
        break;
    }
    return true;
  }
}
