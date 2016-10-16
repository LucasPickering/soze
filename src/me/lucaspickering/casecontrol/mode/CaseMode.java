package me.lucaspickering.casecontrol.mode;

import java.awt.*;
import java.io.Serializable;

public interface CaseMode extends Serializable {

    /**
     * Gets the color that the case LEDs should currently be.
     *
     * @return the desired color
     */
    Color getColor();

}
