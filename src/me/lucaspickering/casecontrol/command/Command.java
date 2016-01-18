package me.lucaspickering.casecontrol.command;

public interface Command {

  /**
   * Gets the name of this command, by which it will be executed.
   *
   * @return the name, in all lower-case letters
   */
  String getName();

  /**
   * Gets the amount of arguments this command takes.
   *
   * @return the exact amount of arguments this command takes
   */
  int getArgumentAmount();

  /**
   * Gets a description of the arguments of this command.
   *
   * @return a String containing the arguments
   */
  String getArgs();

  /**
   * Gets the description of this command and what it does.
   *
   * @return a String containing the description
   */
  String getDesc();

  /**
   * Executes this command with the given arguments.
   *
   * @param args an array of length {@link #getArgumentAmount} containing only lower-case Strings
   * @return true if the program should keep running, false if it should terminate
   */
  boolean execute(String[] args);
}
