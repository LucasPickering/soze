package me.lucaspickering.casecontrol.mode;

import java.awt.Color;

import me.lucaspickering.casecontrol.CaseControl;

public final class CaseModeStatic implements CaseMode {

  @Override
  public Color getColor() {
    return CaseControl.getData().caseStaticColor;
  }
}
