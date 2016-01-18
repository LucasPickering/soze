package me.lucaspickering.casecontrol.command.lcd;

import me.lucaspickering.casecontrol.CaseControl;
import me.lucaspickering.casecontrol.command.Command;
import me.lucaspickering.casecontrol.mode.LcdModeClock;
import me.lucaspickering.casecontrol.mode.LcdModeOff;
import me.lucaspickering.casecontrol.mode.LcdModeTemps;
import me.lucaspickering.casecontrol.mode.LcdModeTodo;

public final class CommandLcdMode implements Command {

  @Override
  public String getName() {
    return "lcdmode";
  }

  @Override
  public int getArgumentAmount() {
    return 1;
  }

  @Override
  public String getArgs() {
    return "<mode>";
  }

  @Override
  public String getDesc() {
    return "Set the mode for the LCD. Valid modes are 'off', 'clock', and 'temps'.";
  }

  @Override
  public boolean execute(String[] args) {
    switch (args[0]) {
      case "off":
        CaseControl.getData().lcdMode = new LcdModeOff();
        System.out.println("LCD mode set to off");
        break;
      case "clock":
        CaseControl.getData().lcdMode = new LcdModeClock();
        System.out.println("LCD mode set to clock");
        break;
      case "temps":
        CaseControl.getData().lcdMode = new LcdModeTemps();
        System.out.println("LCD mode set to temps");
        break;
      case "todo":
        CaseControl.getData().lcdMode = new LcdModeTodo();
        System.out.println("LCD mode set to todo");
        break;
      default:
        System.out.println("That was not a valid mode");
    }
    return true;
  }
}
