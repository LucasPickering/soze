package me.lucaspickering.casecontrol.mode.caseled;

import java.awt.Color;
import java.util.List;

import me.lucaspickering.casecontrol.CaseControl;
import me.lucaspickering.casecontrol.Data;

public final class CaseModeFade extends AbstractCaseMode {

    private int colorIndex;
    private int fadeTicks;
    private int pauseTicks;

    public CaseModeFade() {
        super(EnumCaseMode.FADE);
    }

    @Override
    public Color getColor() {
        final Data data = CaseControl.data();
        final List<Color> colors = data.getCaseFadeColors();
        if (colors.isEmpty()) {
            return Color.BLACK;
        }

        if (fadeTicks < data.getCaseFadeTicks()) {
            fadeTicks++;
        } else if (pauseTicks < data.getCasePauseTicks()) {
            pauseTicks++;
        } else {
            fadeTicks = 0;
            pauseTicks = 0;
            colorIndex++;
        }

        if (colorIndex >= colors.size()) {
            colorIndex = 0;
        }

        float percentDone = (float) fadeTicks / data.getCaseFadeTicks();
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
}