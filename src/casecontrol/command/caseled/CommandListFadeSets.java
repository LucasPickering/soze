package casecontrol.command.caseled;

import java.awt.Color;
import java.util.ArrayList;
import java.util.Map;

import casecontrol.CaseControl;
import casecontrol.command.Command;

public class CommandListFadeSets implements Command {
  @Override
  public String getName() {
    return "listfadesets";
  }

  @Override
  public int getArgumentAmount() {
    return 0;
  }

  @Override
  public String getArgs() {
    return "";
  }

  @Override
  public String getDesc() {
    return "List saved fade color sets.";
  }

  @Override
  public boolean execute(String[] args) {
    for (Map.Entry<String, ArrayList<Color>> entry : CaseControl.getData().savedFades.entrySet()) {
      System.out.println(entry.getKey());
      for (Color color : entry.getValue()) {
        System.out.printf("  (%d, %d, %d)\n", color.getRed(), color.getGreen(), color.getBlue());
      }
    }
    return true;
  }
}
