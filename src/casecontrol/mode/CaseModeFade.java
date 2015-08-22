package casecontrol.mode;

import java.awt.Color;
import java.util.List;

import casecontrol.CaseControl;

public final class CaseModeFade implements CaseMode {

  private static final int PAUSE_TICKS = 50;

  private int colorIndex;
  private int fadeTicks;
  private int pauseTicks;

  @Override
  public Color getColor() {
    final List<Color> colors = CaseControl.getData().caseFadeColors;
    if (colors.size() == 0) {
      return Color.BLACK;
    }

    if (colorIndex >= colors.size()) {
      colorIndex = 0;
    }

    Color lastColor = colors.get(colorIndex);
    Color nextColor = colors.get((colorIndex + 1) % colors.size());
    float percentDone = (float) fadeTicks / CaseControl.getData().caseFadeTicks;
    Color newColor = new Color(
        (int) ((nextColor.getRed() - lastColor.getRed()) * percentDone) + lastColor.getRed(),
        (int) ((nextColor.getGreen() - lastColor.getGreen()) * percentDone) + lastColor.getGreen(),
        (int) ((nextColor.getBlue() - lastColor.getBlue()) * percentDone) + lastColor.getBlue());

    if (fadeTicks < CaseControl.getData().caseFadeTicks) {
      fadeTicks++;
    } else {
      pauseTicks++;
    }
    if (pauseTicks >= PAUSE_TICKS) {
      fadeTicks = 0;
      pauseTicks = 0;
      colorIndex++;
    }

    return newColor;
  }
}
