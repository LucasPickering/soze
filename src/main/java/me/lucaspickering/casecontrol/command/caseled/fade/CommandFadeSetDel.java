package me.lucaspickering.casecontrol.command.caseled.fade;

import java.awt.Color;
import java.util.List;
import java.util.Map;

import me.lucaspickering.casecontrol.CaseControl;
import me.lucaspickering.casecontrol.Data;
import me.lucaspickering.casecontrol.command.AbstractCommand;

public class CommandFadeSetDel extends AbstractCommand {

    @Override
    public String getName() {
        return "del";
    }

    @Override
    public String getArgDesc() {
        return "<name>";
    }

    @Override
    public String getFullDesc() {
        return "Deletes the fade with the given name.";
    }

    @Override
    public boolean execute(String[] args) {
        if (args.length >= 1) {
            final Data data = CaseControl.data();
            final Map<String, List<Color>> savedFades = data.getSavedFades();
            if (savedFades.containsKey(args[0])) {
                savedFades.remove(args[0]);
                System.out.println("Removed " + args[0]);
            } else {
                System.out.println(args[0] + " is not a valid fade set name.");
            }
            return true;
        }
        return false;
    }
}