package me.lucaspickering.casecontrol.mode.lcd;

import me.lucaspickering.casecontrol.Consts;

public enum EnumLcdMode {

    OFF("off", LcdModeOff.class),
    CLOCK("clock", LcdModeClock.class),
    TEMPS("temps", LcdModeTemps.class),
    NHL("nhl", LcdModeNhl.class);

    public final String name;
    private final Class<? extends LcdMode> clazz;
    public final long updatePeriod;

    EnumLcdMode(String name, Class<? extends LcdMode> clazz) {
        this(name, clazz, Consts.DEFAULT_MODE_UPDATE_PERIOD);
    }

    EnumLcdMode(String name, Class<? extends LcdMode> clazz, long updatePeriod) {
        this.name = name;
        this.clazz = clazz;
        this.updatePeriod = updatePeriod;
    }

    public LcdMode instantiateMode() {
        try {
            return clazz.newInstance();
        } catch (InstantiationException | IllegalAccessException e) {
            throw new RuntimeException("Error creating case mode: ", e);
        }
    }
}
