package me.lucaspickering.casecontrol.mode;

public enum EnumLcdMode {

    OFF("off", LcdModeOff.class),
    CLOCK("clock", LcdModeClock.class),
    TEMPS("temps", LcdModeTemps.class),
    NHL("nhl", LcdModeStandings.class);

    public final String name;
    public final Class<? extends LcdMode> clazz;

    EnumLcdMode(String name, Class<? extends LcdMode> clazz) {
        this.name = name;
        this.clazz = clazz;
    }
}
