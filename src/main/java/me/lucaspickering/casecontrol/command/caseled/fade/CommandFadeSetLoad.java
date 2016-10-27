package me.lucaspickering.casecontrol.command.caseled.fade;

import java.awt.Color;
import java.util.List;
import java.util.Map;

import me.lucaspickering.casecontrol.CaseControl;
import me.lucaspickering.casecontrol.Data;
import me.lucaspickering.casecontrol.command.AbstractCommand;

public class CommandFadeSetLoad extends AbstractCommand {

    @Override
    public String getName() {
        return "load";
    }

    @Override
    public String getArgDesc() {
        return "<name>";
    }

    @Override
    public String getFullDesc() {
        return "Sets the current fade set to the saved set of the given name.";
    }

    @Override
    public boolean execute(String[] args) {
        if (args.length >= 1) {
            final String name = args[0];
            final Data data = CaseControl.data();
            final Map<String, List<Color>> savedFades = data.getSavedFades();
            if (savedFades.containsKey(name)) {
                final List<Color> caseFadeColors = data.getCaseFadeColors();
                caseFadeColors.clear();
                caseFadeColors.addAll(savedFades.get(name));
                System.out.println("Loaded " + name);
            } else {
                System.out.println("No fade set by the name " + name);
            }
            return true;
        }
        return false;
    }
}
