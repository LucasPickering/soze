package casecontrol.command;

public enum EnumAlias {

  CLOCK ("clock", "lcdmode clock"), TEMPS("temps", "lcdmode temps");

  public final String name;
  public final String command;

  EnumAlias(String name, String command){
    this.name = name;
    this.command = command;
  }
}
