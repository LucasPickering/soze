package me.lucaspickering.casecontrol;

import java.io.File;
import java.io.FileInputStream;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.ObjectInputStream;
import java.io.ObjectOutputStream;
import java.util.Arrays;
import java.util.Scanner;

import me.lucaspickering.casecontrol.command.Command;
import me.lucaspickering.casecontrol.command.EnumAlias;
import me.lucaspickering.casecontrol.command.EnumCommand;

public final class CaseControl {

  public static final CaseControl caseControl = new CaseControl();
  private final ModeThread modeThread = new ModeThread();
  private final SerialThread serialThread = new SerialThread();
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
    Runtime.getRuntime().addShutdownHook(serialThread);
    loadData();
    modeThread.start();
    serialThread.start();
    Scanner scanner = new Scanner(System.in);
    do {
      System.out.print(">");
    } while (runInput(scanner.nextLine().toLowerCase()));
    saveData();
    serialThread.terminate();
    modeThread.terminate();
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
    for (EnumAlias alias : EnumAlias.values()) {
      if (commandName.equals(alias.name)) {
        for(String aliasCommand:alias.commands){
          if(!runInput(aliasCommand)){
            return false;
          }
        }
        return true;
      }
    }
    for (EnumCommand enumCommand : EnumCommand.values()) {
      if (commandName.equals(enumCommand.command.getName())) {
        command = enumCommand.command;
        break;
      }
    }
    if (command == null) {
      System.out.println(commandName + " is not a valid command");
    } else if (splits.length <= command.getArgumentAmount()) {
      System.out.println("Not enough arguments");
    } else {
      final boolean result = command.execute(Arrays.copyOfRange(splits, 1, splits.length));
      saveData();
      return result;
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