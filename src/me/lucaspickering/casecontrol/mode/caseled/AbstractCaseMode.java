package me.lucaspickering.casecontrol.mode.caseled;

abstract class AbstractCaseMode implements CaseMode {

    private final EnumCaseMode caseMode;

    AbstractCaseMode(EnumCaseMode caseMode) {
        this.caseMode = caseMode;
    }

    public void init(String... args) {
        // Do nothing by default
    }

    @Override
    public final EnumCaseMode getMode() {
        return caseMode;
    }

    @Override
    public String toString() {
        return caseMode.name;
    }
}
