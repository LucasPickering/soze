package me.lucaspickering.casecontrol.mode.lcd;

import me.lucaspickering.casecontrol.Funcs;

public final class LcdModeTemps extends AbstractLcdMode {

    @Override
    public EnumLcdMode getMode() {
        return EnumLcdMode.TEMPS;
    }

    @Override
    public String[] getText() {
        final int[] sfData = Funcs.getSpeedFanData();

        // \u00df is the degree symbol
        return new String[]{
            String.format("Fan: %d RPM", sfData[5]),
            String.format("CPU: %d\u00dfC %d\u00dfC", sfData[0], sfData[1]),
            String.format("     %d\u00dfC %d\u00dfC", sfData[2], sfData[3]),
            String.format("GPU: %d\u00dfC", sfData[4])
        };
    }

    @Override
    public String toString() {
        return "Temps";
    }
}
