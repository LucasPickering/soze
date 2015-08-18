package casecontrol.command.caseled;

import java.awt.Color;

import casecontrol.CaseControl;
import casecontrol.Data;
import casecontrol.command.Command;

public final class CommandAddFadeColor implements Command {

  @Override
  public String getName() {
    return "addfade";
  }

  @Override
  public int getArgumentAmount() {
    return 3;
  }

  @Override
  public String getArgs() {
    return "<red> <green> <blue>";
  }

  @Override
  public String getDesc() {
    return "Add the given RGB color to the end of the fade color list.";
  }

  @Override
  public boolean execute(String[] args) {
    final int red;
    final int green;
    final int blue;
    try {
      red = CaseControl.clamp(new Integer(args[0]), 0, 255);
      green = CaseControl.clamp(new Integer(args[1]), 0, 255);
      blue = CaseControl.clamp(new Integer(args[2]), 0, 255);
    } catch (NumberFormatException e) {
      System.out.println("RGB values must be numbers");
      return true;
    }
    Data.caseFadeColors.add(new Color(red, green, blue));
    System.out.printf("Case fade color (%d, %d, %d) added at %d\n", red, green, blue,
        Data.caseFadeColors.size() - 1);
    return true;
  }
}
