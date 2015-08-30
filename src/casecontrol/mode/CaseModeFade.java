package casecontrol.mode;

import java.awt.*;
import java.util.List;

import casecontrol.CaseControl;
import casecontrol.Data;

public final class CaseModeFade implements CaseMode {

  private int colorIndex;
  private int fadeTicks;

  @Override
  public Color getColor() {
    final Data data = CaseControl.getData();
    final List<Color> colors = data.caseFadeColors;
    if (colors.isEmpty()) {
      return Color.BLACK;
    }

    if (fadeTicks >= data.caseFadeTicks) {
      fadeTicks = 0;
      colorIndex++;
    }

    if (colorIndex >= colors.size()) {
      colorIndex = 0;
    }

    Color last = colors.get(colorIndex);
    Color next = colors.get((colorIndex + 1) % colors.size());

    final float percentDone = (float) fadeTicks / data.caseFadeTicks;
    fadeTicks++;

    return new Color(
            (int) ((next.getRed() - last.getRed()) * percentDone) + last.getRed(),
            (int) ((next.getGreen() - last.getGreen()) * percentDone) + last.getGreen(),
            (int) ((next.getBlue() - last.getBlue()) * percentDone) + last.getBlue());
  }
}
