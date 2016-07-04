package me.lucaspickering.casecontrol.command;

public interface Command {

	/**
	 * Gets the name of this command, by which it will be executed.
	 *
	 * @return the name, in all lower-case letters
	 */
	String getName();

	/**
	 * Is the given string a valid sub-command for this command?
	 *
	 * @return true if the given sub-command is valid, false otherwise
	 */
	boolean isSubcommand(String subcommand);

	/**
	 * Gets the sub-command for the given string.
	 *
	 * @param subcommand the sub-command to get by name
	 * @return the sub-command, or {@code null} if there is no sub-command for this command by the
	 * given name
	 */
	Command getSubcommand(String subcommand);

	/**
	 * Prints a list of all available sub-commands for this command, and their purposes.
	 */
	void printSubcommands();

	/**
	 * Gets a brief description of this command's arguments. An example would be "<mode>" for "case
	 * mode".
	 *
	 * @return the brief description, or {@code null} if this command takes no arguments
	 */
	String getArgDesc();

	/**
	 * Gets a full sentence (or more!) describing what this command does.
	 *
	 * @return the full description
	 */
	String getFullDesc();

	/**
	 * Executes this command with the given arguments.
	 *
	 * @param args an array containg the arguments for this command
	 * @return true if the execution was succesful, false otherwise (in which case help dialogue will
	 * be printed)
	 */
	boolean execute(String[] args);

}
