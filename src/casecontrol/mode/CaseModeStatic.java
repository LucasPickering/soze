package casecontrol.mode;

import java.awt.Color;

import casecontrol.CaseControl;

public final class CaseModeStatic implements CaseMode {

  @Override
  public Color getColor() {
    return CaseControl.getData().caseStaticColor;
  }
}
