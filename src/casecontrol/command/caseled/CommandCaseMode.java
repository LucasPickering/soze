package casecontrol.command.caseled;

import casecontrol.CaseControl;
import casecontrol.command.Command;
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
    return "Set the mode for the case LEDs. Valid modes are 'off', 'static', and 'fade'";
  }

  @Override
  public boolean execute(String[] args) {
    switch (args[0]) {
      case "off":
        CaseControl.getData().caseMode = new CaseModeOff();
        System.out.println("Case LED mode set to off");
        break;
      case "static":
        CaseControl.getData().caseMode = new CaseModeStatic();
        System.out.println("Case LED mode set to static");
        break;
      case "fade":
        CaseControl.getData().caseMode = new CaseModeFade();
        System.out.println("Case LED mode set to fade");
        break;
      default:
        System.out.println("That was not a valid case LED mode");
    }
    return true;
  }
}
