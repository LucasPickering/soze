package casecontrol.mode;

public final class LcdModeTemps extends AbstractLcdMode {

  @Override
  public String[] getText() {
    // ﬂ gets decoded and recoded into the degree symbol
    text[0] = String.format("Fan: %d RPM", 9999);
    text[1] = String.format("CPU: %dﬂC %dﬂC", 99, 99);
    text[2] = String.format("     %dﬂC %dﬂC", 99, 99);
    text[3] = String.format("GPU: %dﬂC", 99);
    return text;
  }
}
