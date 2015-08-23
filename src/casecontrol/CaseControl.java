package casecontrol;

import java.io.File;
import java.io.FileInputStream;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.ObjectInputStream;
import java.io.ObjectOutputStream;
import java.util.Arrays;
import java.util.Scanner;

import casecontrol.command.Command;
import casecontrol.command.caseled.CommandAddFadeColor;
import casecontrol.command.caseled.CommandCaseMode;
import casecontrol.command.caseled.CommandCaseStaticColor;
import casecontrol.command.caseled.CommandClearFade;
import casecontrol.command.caseled.CommandFadeList;
import casecontrol.command.caseled.CommandListSavedFade;
import casecontrol.command.caseled.CommandLoadFade;
import casecontrol.command.caseled.CommandRemoveFade;
import casecontrol.command.caseled.CommandRemoveFadeColor;
import casecontrol.command.caseled.CommandSaveFade;
import casecontrol.command.caseled.CommandSetFadeTicks;
import casecontrol.command.general.CommandExit;
import casecontrol.command.general.CommandHelp;
import casecontrol.command.lcd.CommandLcdColor;
import casecontrol.command.lcd.CommandLcdMode;

public final class CaseControl {

  public static final CaseControl caseControl = new CaseControl();
  public static final Command[] commands = new Command[]{
      new CommandExit(), new CommandHelp(), new CommandCaseMode(), new CommandCaseStaticColor(),
      new CommandFadeList(), new CommandAddFadeColor(), new CommandRemoveFadeColor(),
      new CommandSaveFade(), new CommandLoadFade(), new CommandRemoveFade(), new CommandClearFade(),
      new CommandListSavedFade(), new CommandSetFadeTicks(), new CommandLcdMode(),
      new CommandLcdColor()
  };
  private final LoopThread loopThread = new LoopThread();
  private Data data = new Data();

  public static void main(String[] args) {
    caseControl.inputLoop();
  }

  public static Data getData() {
    return caseControl.data;
  }

  /**
   * Constantly receives input from the user. Main loop of the program.
   */
  private void inputLoop() {
    loadData();
    loopThread.start();
    Scanner scanner = new Scanner(System.in);
    do {
      System.out.print(">");
    } while (runInput(scanner.nextLine().toLowerCase()));
    loopThread.terminate();
    saveData();
    System.out.println("Exiting...");
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
    if (command == null) {
      System.out.println(commandName + " is not a valid command");
    } else if (splits.length <= command.getArgumentAmount()) {
      System.out.println("Not enough arguments");
    } else {
      return command.execute(Arrays.copyOfRange(splits, 1, splits.length));
    }
    return true;
  }

  private void saveData() {
    try {
      FileOutputStream fileOut = new FileOutputStream(Data.DATA_FILE);
      ObjectOutputStream objectOut = new ObjectOutputStream(fileOut);

      objectOut.writeObject(data);

      objectOut.close();
      fileOut.close();
    } catch (IOException e) {
      e.printStackTrace();
    }
  }

  private void loadData() {
    try {
      if (new File(Data.DATA_FILE).exists()) {
        FileInputStream fileIn = new FileInputStream(Data.DATA_FILE);
        ObjectInputStream objectIn = new ObjectInputStream(fileIn);

        data = (Data) objectIn.readObject();

        objectIn.close();
        fileIn.close();
      }
    } catch (IOException | ClassNotFoundException e) {
      e.printStackTrace();
    }
  }
}
