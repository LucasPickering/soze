package casecontrol.command;

import casecontrol.CaseControl;

public final class CommandHelp implements Command {
  @Override
  public String getName() {
    return "help";
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
    return "Print the help dialog.";
  }

  @Override
  public boolean execute(String[] args) {
    for (Command command : CaseControl.commands) {
      System.out.printf("%s %s - %s\n", command.getName(), command.getArgs(), command.getDesc());
    }
    return true;
  }
}
