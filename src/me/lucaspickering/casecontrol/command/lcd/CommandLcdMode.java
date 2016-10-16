package me.lucaspickering.casecontrol.command.lcd;

import me.lucaspickering.casecontrol.CaseControl;
import me.lucaspickering.casecontrol.command.AbstractCommand;
import me.lucaspickering.casecontrol.mode.LcdModeClock;
import me.lucaspickering.casecontrol.mode.LcdModeOff;
import me.lucaspickering.casecontrol.mode.LcdModeTemps;

public class CommandLcdMode extends AbstractCommand {

    @Override
    public String getName() {
        return "mode";
    }

    @Override
    public String getArgDesc() {
        return "<mode>";
    }

    @Override
    public String getFullDesc() {
        return "Sets the LCD mode.";
    }

    @Override
    public boolean execute(String[] args) {
        if (args.length >= 1) {
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
                default:
                    System.out.println("That was not a valid mode");
            }
            return true;
        }
        return false;
    }
}
