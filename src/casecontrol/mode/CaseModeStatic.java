package casecontrol.mode;

import java.awt.*;

import casecontrol.Data;

public final class CaseModeStatic implements CaseMode {

  @Override
  public Color getColor() {
    return Data.caseStaticColor;
  }
}
