package me.lucaspickering.casecontrol.mode.caseled;

import java.awt.*;
import java.util.List;

import me.lucaspickering.casecontrol.CaseControl;
import me.lucaspickering.casecontrol.Data;

public final class CaseModeFade implements CaseMode {

    private int colorIndex;
    private int fadeTicks;
    private int pauseTicks;

    @Override
    public EnumCaseMode getMode() {
        return EnumCaseMode.FADE;
    }

    @Override
    public Color getColor() {
        final Data data = CaseControl.data();
        final List<Color> colors = data.caseFadeColors;
        if (colors.isEmpty()) {
            return Color.BLACK;
        }

        if (fadeTicks < data.caseFadeTicks) {
            fadeTicks++;
        } else if (pauseTicks < data.casePauseTicks) {
            pauseTicks++;
        } else {
            fadeTicks = 0;
            pauseTicks = 0;
            colorIndex++;
        }

        if (colorIndex >= colors.size()) {
            colorIndex = 0;
        }

        float percentDone = (float) fadeTicks / data.caseFadeTicks;
        if (percentDone > 1F) {
            percentDone = 1F;
        }
        Color last = colors.get(colorIndex);
        Color next = colors.get((colorIndex + 1) % colors.size());

        fadeTicks++;

        return new Color(
            (int) ((next.getRed() - last.getRed()) * percentDone) + last.getRed(),
            (int) ((next.getGreen() - last.getGreen()) * percentDone) + last.getGreen(),
            (int) ((next.getBlue() - last.getBlue()) * percentDone) + last.getBlue());
    }

    @Override
    public String toString() {
        return "Fade";
    }
}
