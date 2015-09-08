package casecontrol.command;

public enum EnumAlias {

  OFF("off", "casemode off", "lcdmode off"),
  STATIC("static", "casemode static"), FADE("fade", "casemode fade"),
  CLOCK("clock", "lcdmode clock"), TEMPS("temps", "lcdmode temps"), TODO("todo", "lcdmode todo");

  public final String name;
  public final String[] commands;

  EnumAlias(String name, String... commands) {
    this.name = name;
    this.commands = commands;
  }
}
