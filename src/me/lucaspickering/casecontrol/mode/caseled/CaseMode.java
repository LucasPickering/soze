package me.lucaspickering.casecontrol.mode.caseled;

import java.awt.Color;

public interface CaseMode {

    /**
     * Initialize this mode using the given arguments.
     *
     * @param args the arguments to initialize with
     */
    void init(String... args);

    /**
     * Gets the {@link EnumCaseMode} for this mode.
     *
     * @return the appropriate {@link EnumCaseMode}
     */
    EnumCaseMode getMode();

    /**
     * Gets the color that the case LEDs should currently be.
     *
     * @return the desired color
     */
    Color getColor();
}
