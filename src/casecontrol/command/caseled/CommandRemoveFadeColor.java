package casecontrol.command.caseled;

import casecontrol.Data;
import casecontrol.command.Command;

public final class CommandRemoveFadeColor implements Command {
  @Override
  public String getName() {
    return "remfade";
  }

  @Override
  public int getArgumentAmount() {
    return 1;
  }

  @Override
  public String getArgs() {
    return "<index>";
  }

  @Override
  public String getDesc() {
    return "Remove the color at the given index from the case fade color list.";
  }

  @Override
  public boolean execute(String[] args) {
    final int index;
    try {
      index = new Integer(args[0]);
    } catch (NumberFormatException e) {
      System.out.println("Index value must be a number");
      return true;
    }
    if (0 <= index && index < Data.caseFadeColors.size()) {
      Data.caseFadeColors.remove(index);
      System.out.printf("Case fade color at %d removed\n", index);
    } else {
      System.out.println("Invalid index: " + index);
    }
    return true;
  }
}
