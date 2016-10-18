package me.lucaspickering.casecontrol.command.caseled.fade;

import me.lucaspickering.casecontrol.CaseControl;
import me.lucaspickering.casecontrol.Consts;
import me.lucaspickering.casecontrol.Data;
import me.lucaspickering.casecontrol.command.AbstractCommand;

public class CommandFadeTiming extends AbstractCommand {

    public CommandFadeTiming() {
        super(new CommandFadeTimingTrans(), new CommandFadeTimingPause());
    }

    @Override
    public String getName() {
        return "timing";
    }

    @Override
    public String getArgDesc() {
        return null;
    }

    @Override
    public String getFullDesc() {
        return "Contains sub-commands for fade timing-related activities.";
    }

    @Override
    public boolean execute(String[] args) {
        // Print current fade timing settings, then return false to print help
        Data data = CaseControl.data();
        System.out.println("Fade timings:");
        System.out.printf("  Transition: %d ticks (Min %d; Max %d)\n",
                          data.getCaseFadeTicks(), Consts.MIN_FADE_TICKS, Consts.MAX_FADE_TICKS);
        System.out.printf("  Pause: %d ticks (Min %d; Max %d)\n",
                          data.getCasePauseTicks(), Consts.MIN_PAUSE_TICKS, Consts.MAX_PAUSE_TICKS);
        return false;
    }
}
