package casecontrol.mode;

import java.awt.Color;
import java.io.Serializable;

public final class CaseModeOff implements CaseMode {

  @Override
  public Color getColor() {
    return Color.BLACK;
  }
}
