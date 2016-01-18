package me.lucaspickering.casecontrol.command.caseled;

import java.awt.Color;

import me.lucaspickering.casecontrol.CaseControl;
import me.lucaspickering.casecontrol.Funcs;
import me.lucaspickering.casecontrol.command.Command;

public final class CommandAddFadeColor implements Command {

  @Override
  public String getName() {
    return "addfade";
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
    return "Add the given color to the end of the fade color list.";
  }

  @Override
  public boolean execute(String[] args) {
    Color color = Funcs.getColor(args[0]);
    if (color != null) {
      CaseControl.getData().caseFadeColors.add(color);
      System.out.printf("Case fade color (%d, %d, %d) added at %d\n", color.getRed(),
          color.getGreen(), color.getBlue(), CaseControl.getData().caseFadeColors.size() - 1);
    }
    return true;
  }
}
