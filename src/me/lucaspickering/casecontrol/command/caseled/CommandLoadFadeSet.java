package me.lucaspickering.casecontrol.command.caseled;

import me.lucaspickering.casecontrol.CaseControl;
import me.lucaspickering.casecontrol.Data;
import me.lucaspickering.casecontrol.command.Command;

public final class CommandLoadFadeSet implements Command {
  @Override
  public String getName() {
    return "loadfadeset";
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
    return "Load the fade color set of the given name.";
  }

  @Override
  public boolean execute(String[] args) {
    final String name = args[0];
    final Data data = CaseControl.getData();
    if (data.savedFades.containsKey(name)) {
      data.caseFadeColors.clear();
      data.caseFadeColors.addAll(data.savedFades.get(name));
      System.out.println("Loaded " + name);
    } else {
      System.out.println("No fade set by the name " + name);
    }
    return true;
  }
}
