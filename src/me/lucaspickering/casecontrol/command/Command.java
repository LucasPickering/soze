package me.lucaspickering.casecontrol.command;

public interface Command {

	/**
	 * Gets the name of this command, by which it will be executed.
	 *
	 * @return the name, in all lower-case letters
	 */
	String getName();

	/**
	 * Does this command have subcommands? If true, the first string after the command will be treated
	 * as a subcommand, rather than the first argument, and arguments will start at the third string.
	 *
	 * @return true if this command has subcommands, false otherwise
	 */
	boolean hasSubCommands();

	/**
	 * Is the given string a valid sub-command for this command?
	 *
	 * @return true if the given sub-command is valid, false otherwise
	 */
	boolean isSubCommand(String subcommand);

	/**
	 * Gets a brief description of this command's arguments. An example would be "<mode>" for "case
	 * mode".
	 *
	 * @return the brief description
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
