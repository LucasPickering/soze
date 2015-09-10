package casecontrol.command.caseled;

import casecontrol.CaseControl;
import casecontrol.Data;
import casecontrol.Funcs;
import casecontrol.command.Command;

public final class CommandSetPauseTicks implements Command {

    @Override
    public String getName() {
        return "pauseticks";
    }

    @Override
    public int getArgumentAmount() {
        return 1;
    }

    @Override
    public String getArgs() {
        return "<ticks>";
    }

    @Override
    public String getDesc() {
        return "Set the amount of ticks the fade should pause for on each color.";
    }

    @Override
    public boolean execute(String[] args) {
        final int ticks;
        try {
            ticks = Funcs.clamp(new Integer(args[0]), Data.MIN_PAUSE_TICKS, Data.MAX_PAUSE_TICKS);
        } catch (NumberFormatException e) {
            System.out.println("Tick value must be a number");
            return true;
        }
        CaseControl.getData().casePauseTicks = ticks;
        System.out.println("Pause ticks set to " + ticks);
        return true;
    }
}
