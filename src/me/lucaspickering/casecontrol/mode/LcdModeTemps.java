package me.lucaspickering.casecontrol.mode;

import me.lucaspickering.casecontrol.Funcs;

public final class LcdModeTemps extends AbstractLcdMode {

	@Override
	public String[] getText() {
		final int[] data = Funcs.getSpeedFanData();

		// /u00df is the degree symbol
		text[0] = String.format("Fan: %d RPM", data[5]);
		text[1] = String.format("CPU: %d\u00dfC %d\u00dfC", data[0], data[1]);
		text[2] = String.format("     %d\u00dfC %d\u00dfC", data[2], data[3]);
		text[3] = String.format("GPU: %d\u00dfC", data[4]);
		return text;
	}

	@Override
	public String toString() {
		return "Temps";
	}
}
