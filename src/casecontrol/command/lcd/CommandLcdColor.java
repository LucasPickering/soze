package casecontrol.command.lcd;

import java.awt.Color;

import casecontrol.CaseControl;
import casecontrol.Funcs;
import casecontrol.command.Command;

public final class CommandLcdColor implements Command {
  @Override
  public String getName() {
    return "lcdcolor";
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
    return "Set the LCD color to the given color.";
  }

  @Override
  public boolean execute(String[] args) {
    final Color color = Funcs.getColor(args[0]);
    if (color != null) {
      CaseControl.getData().lcdColor = color;
      System.out.printf("LCD color set to (%d, %d, %d)\n", color.getRed(),
          color.getGreen(), color.getBlue());
    }
    return true;
  }
}
