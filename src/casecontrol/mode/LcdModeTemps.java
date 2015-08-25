package casecontrol.mode;

import casecontrol.Funcs;

public final class LcdModeTemps extends AbstractLcdMode {

  @Override
  public String[] getText() {
    final int[] data = Funcs.getSpeedFanData();

    // ﬂ gets decoded and recoded into the degree symbol
    text[0] = String.format("Fan: %d RPM", data[5]);
    text[1] = String.format("CPU: %dﬂC %dﬂC", data[0], data[1]);
    text[2] = String.format("     %dﬂC %dﬂC", data[2], data[3]);
    text[3] = String.format("GPU: %dﬂC", data[4]);
    return text;
  }
}
