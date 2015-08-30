package casecontrol.mode;

import casecontrol.Funcs;

public final class LcdModeTemps extends AbstractLcdMode {

  @Override
  public String[] getText() {
    final int[] data = Funcs.getSpeedFanData();

    // ? becomes the degree symbol
    text[0] = String.format("Fan: %d RPM", data[5]);
    text[1] = String.format("CPU: %d?C %d?C", data[0], data[1]);
    text[2] = String.format("     %d?C %d?C", data[2], data[3]);
    text[3] = String.format("GPU: %d?C", data[4]);
    return text;
  }
}
