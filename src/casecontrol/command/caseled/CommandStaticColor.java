package casecontrol.command.caseled;

import java.awt.Color;

import casecontrol.CaseControl;
import casecontrol.Funcs;
import casecontrol.command.Command;

public final class CommandStaticColor implements Command {
  @Override
  public String getName() {
    return "static";
  }

  @Override
  public int getArgumentAmount() {
    return 1;
  }

  @Override
  public String getArgs() {
    return "<color>";
  }

  @Override
  public String getDesc() {
    return "Set the LED static color to the given color.";
  }

  @Override
  public boolean execute(String[] args) {
    Color color = Funcs.getColor(args[0]);
    if(color != null) {
      CaseControl.getData().caseStaticColor = color;
      System.out.printf("Case static color set to (%d, %d, %d)\n", color.getRed(),
          color.getGreen(), color.getBlue());
    }
    return true;
  }
}
