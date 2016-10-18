package me.lucaspickering.casecontrol.mode.caseled;

import me.lucaspickering.casecontrol.Consts;

public enum EnumCaseMode {

    OFF("off", CaseModeOff.class),
    STATIC("static", CaseModeStatic.class),
    FADE("fade", CaseModeFade.class, 30L); // Update every 30 ms

    public final String name;
    private final Class<? extends CaseMode> clazz;
    public final long updatePeriod;

    EnumCaseMode(String name, Class<? extends CaseMode> clazz) {
        this(name, clazz, Consts.DEFAULT_MODE_UPDATE_PERIOD);
    }

    EnumCaseMode(String name, Class<? extends CaseMode> clazz, long updatePeriod) {
        this.name = name;
        this.clazz = clazz;
        this.updatePeriod = updatePeriod;
    }

    public CaseMode instantiateMode() {
        try {
            return clazz.newInstance();
        } catch (InstantiationException | IllegalAccessException e) {
            throw new RuntimeException("Error creating case mode: ", e);
        }
    }
}
