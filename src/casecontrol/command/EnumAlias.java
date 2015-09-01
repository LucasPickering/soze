package casecontrol.command;

public enum EnumAlias {

  STATIC("static", "casemode static"), FADE("fade", "casemode fade"),
  CLOCK("clock", "lcdmode clock"), TEMPS("temps", "lcdmode temps"), TODO("todo", "lcdmode todo");

  public final String name;
  public final String command;

  EnumAlias(String name, String command) {
    this.name = name;
    this.command = command;
  }
}
