package me.lucaspickering.casecontrol.command.caseled.fade;

import me.lucaspickering.casecontrol.CaseControl;
import me.lucaspickering.casecontrol.Data;
import me.lucaspickering.casecontrol.command.AbstractCommand;

public class CommandFadeSetLoad extends AbstractCommand {

  @Override
  public String getName() {
    return "loadfadeset";
  }

  @Override
  public String getArgDesc() {
    return "<name>";
  }

  @Override
  public String getFullDesc() {
    return "Sets the current fade set to the saved set of the given name.";
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
