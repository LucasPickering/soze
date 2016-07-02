package me.lucaspickering.casecontrol.command;

import me.lucaspickering.casecontrol.command.caseled.CommandCaseColor;
import me.lucaspickering.casecontrol.command.caseled.CommandCaseMode;

public class CommandCase extends AbstractCommand {

  protected CommandCase() {
    super(new CommandCaseMode(), new CommandCaseColor());
  }

  @Override
  public String getName() {
    return "case";
  }

  @Override
  public String getArgDesc() {
    return "";
  }

  @Override
  public String getFullDesc() {
    return "Contains sub-commands for case-related activities.";
  }
}
