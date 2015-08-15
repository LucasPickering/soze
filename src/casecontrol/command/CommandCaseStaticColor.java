package casecontrol.command;

import java.awt.*;

import casecontrol.CaseControl;
import casecontrol.Data;

public final class CommandCaseStaticColor implements Command {
  @Override
  public String getName() {
    return "casestatic";
  }

  @Override
  public int getArgumentAmount() {
    return 3;
  }

  @Override
  public String getArgs(){
    return "<red> <green> <blue>";
  }

  @Override
  public String getDesc(){
    return "Set the LED static color to the given RGB color.";
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
    Data.caseStaticColor = new Color(red, green, blue);
    System.out.printf("Case static color set to (%d, %d, %d)\n", red, green, blue);
    return true;
  }
}
