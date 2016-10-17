package me.lucaspickering.casecontrol.mode;

public enum EnumCaseMode {

    OFF("off", CaseModeOff.class),
    STATIC("static", CaseModeStatic.class),
    FADE("fade", CaseModeFade.class);

    public final String name;
    public final Class<? extends CaseMode> clazz;

    EnumCaseMode(String name, Class<? extends CaseMode> clazz) {
        this.name = name;
        this.clazz = clazz;
    }
}
