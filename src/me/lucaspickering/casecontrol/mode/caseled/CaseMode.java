package me.lucaspickering.casecontrol.mode.caseled;

import java.awt.*;
import java.io.Serializable;

public interface CaseMode extends Serializable {

    /**
     * Gets the {@link EnumCaseMode} for this mode.
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
