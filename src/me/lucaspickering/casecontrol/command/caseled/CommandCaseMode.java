package me.lucaspickering.casecontrol.command.caseled;

import java.util.Arrays;

import me.lucaspickering.casecontrol.CaseControl;
import me.lucaspickering.casecontrol.command.AbstractCommand;
import me.lucaspickering.casecontrol.mode.caseled.EnumCaseMode;

public class CommandCaseMode extends AbstractCommand {

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
        // List all the possible modes
        final CharSequence[] names =
            Arrays.stream(EnumCaseMode.values()).map(m -> m.name).toArray(CharSequence[]::new);
        return "Set the mode for the case LEDs. Valid modes are: " + String.join(", ", names);
    }

    @Override
    public boolean execute(String[] args) {
        if (args.length >= 1) {
            final String mode = args[0];
            for (EnumCaseMode caseMode : EnumCaseMode.values()) {
                if (mode.equals(caseMode.name)) {
                    CaseControl.data().setCaseMode(caseMode);
                    System.out.printf("Case LED mode set to %s\n", caseMode.name);
                    return true; // Succesfully completed
                }
            }
            System.out.printf("Invalid mode: %s\n", mode);
        }
        return false;
    }
}
