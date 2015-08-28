package casecontrol.command.caseled;

import casecontrol.CaseControl;
import casecontrol.Data;
import casecontrol.command.Command;

public final class CommandRemoveFadeSet implements Command {
  @Override
  public String getName() {
    return "remfadeset";
  }

  @Override
  public int getArgumentAmount() {
    return 1;
  }

  @Override
  public String getArgs() {
    return "<name>";
  }

  @Override
  public String getDesc() {
    return "Remove the fade with the given name from the saved fade list.";
  }

  @Override
  public boolean execute(String[] args) {
    final String name = args[0];
    final Data data = CaseControl.getData();
    if (data.savedFades.containsKey(name)) {
      data.savedFades.remove(name);
      System.out.println("Removed " + name);
    } else {
      System.out.println("No fade set by the name " + name);
    }
    return true;
  }
}
