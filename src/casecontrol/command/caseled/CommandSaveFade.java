package casecontrol.command.caseled;

import java.awt.Color;
import java.util.ArrayList;

import casecontrol.CaseControl;
import casecontrol.Data;
import casecontrol.command.Command;

public final class CommandSaveFade implements Command {
  @Override
  public String getName() {
    return "savefade";
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
    return "Save the current fade color set with the given name.";
  }

  @Override
  @SuppressWarnings("unchecked")
  public boolean execute(String[] args) {
    final Data data = CaseControl.getData();
    if (data.caseFadeColors.isEmpty()) {
      System.out.println("Fade list is empty, nothing saved");
    } else {
      final String name = args[0];
      data.savedFades.put(name, (ArrayList<Color>) data.caseFadeColors.clone());
      System.out.println("Saved current fade set under " + name);
    }
    return true;
  }
}
