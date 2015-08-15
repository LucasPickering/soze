package casecontrol;

import java.util.Arrays;
import java.util.Scanner;

import casecontrol.command.Command;
import casecontrol.command.CommandCaseMode;
import casecontrol.command.CommandCaseStaticColor;
import casecontrol.command.CommandExit;
import casecontrol.command.CommandHelp;

public final class CaseControl {

  public static final CaseControl main = new CaseControl();
  public static final Command[] commands = new Command[]{
      new CommandExit(),
      new CommandHelp(),
      new CommandCaseStaticColor(),
      new CommandCaseMode()
  };

  public static void main(String[] args) {
    main.inputLoop();
  }

  /**
   * Clamps the given number to the given range.
   *
   * @param n   the number to be clamped
   * @param min the minimum of the range (inclusive)
   * @param max the maximum of the range (inclusive)
   * @return n clamped to the range [0, 255]
   */
  public static int clamp(int n, int min, int max) {
    return n < min ? min : n > max ? max : n;
  }

  /**
   * Constantly receives input from the user. Main loop of the program.
   */
  private void inputLoop() {
    Scanner scanner = new Scanner(System.in);
    do {
      System.out.print(">");
    } while (runInput(scanner.nextLine().toLowerCase()));
  }

  /**
   * Interprets input from the user.
   *
   * @param input the input from the user, must be lower case
   * @return true if the program should keep running, false if it should terminate
   */
  private boolean runInput(String input) {
    String[] splits = input.split(" ");
    String commandName = splits[0];
    Command command = null;
    for (Command command1 : commands) {
      if (commandName.equals(command1.getName())) {
        command = command1;
        break;
      }
    }
    if (command != null && splits.length > command.getArgumentAmount()) {
      return command.execute(Arrays.copyOfRange(splits, 1, splits.length));
    }
    System.out.println(commandName + " is not a valid command");
    return true;
  }
}
