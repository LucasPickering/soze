package me.lucaspickering.casecontrol;

import java.io.File;
import java.io.FileInputStream;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.ObjectInputStream;
import java.io.ObjectOutputStream;
import java.util.Arrays;
import java.util.HashMap;
import java.util.Map;
import java.util.Scanner;

import me.lucaspickering.casecontrol.command.Command;
import me.lucaspickering.casecontrol.command.EnumCommand;

public final class CaseControl {

    private static final CaseControl caseControl = new CaseControl();
    private static boolean run = true;

    private final ModeThread modeThread = new ModeThread();
    private final SerialThread serialThread = new SerialThread();
    private Data data = new Data();
    private final Map<String, Command> commands = new HashMap<>();

    public static void main(String[] args) {
        caseControl.inputLoop();
    }

    public static Data getData() {
        return caseControl.data;
    }

    public static void stop() {
        run = false;
    }

    /**
     * Constantly receives input from the user. Main loop of the program.
     */
    private void inputLoop() {
        Runtime.getRuntime().addShutdownHook(serialThread); // Tell the serial thread when we stop
        loadData(); // Load saved data (if possible)
        modeThread.start(); // Start the thread that does color/text calculations
        serialThread.start(); // Start the thread that communicates over the serial port
        // Register all top-level commands
        for (EnumCommand command : EnumCommand.values()) {
            commands.put(command.command.getName(), command.command);
        }
        Scanner scanner = new Scanner(System.in); // Scanner to get input from the command lin
        do {
            System.out.print(">");
            runInput(scanner.nextLine().toLowerCase());
            saveData(); // Save data after each command (it's cheap)
        } while (run);
        serialThread.terminate();
        modeThread.terminate();
        System.out.println("Exiting...");
    }

    /**
     * Interprets input from the user.
     *
     * @param input the input from the user, must be lower case
     */
    private void runInput(String input) {
        String[] splits = input.split(" "); // Split the input into words.
        String commandName = splits[0];
        if (commands.containsKey(commandName)) {
            Command command = commands.get(commandName);
            // Keep going down the array until the next string in there isn't a sub-command
            int i;
            for (i = 1; i < splits.length; i++) {
                if (command.isSubcommand(splits[i])) {
                    command = command.getSubcommand(splits[i]);
                } else {
                    break;
                }
            }
            // command is now the lowest-level sub-command possible. All remaining strings in splits
            // are arguments (if there are any at all).

            // Execute command with arguments
            if (!command.execute(Arrays.copyOfRange(splits, i, splits.length))) {
                if (command.hasSubcommands()) {
                    System.out.println("Available sub-commands:");
                    command.printSubcommands();
                } else {
                    Funcs.printCommandInfo(command);
                }
            }
        } else {
            System.out.println("That was not a valid command. Maybe try \'help\'.");
        }
    }

    private void saveData() {
        try {
            FileOutputStream fileOut = new FileOutputStream(Data.DATA_FILE);
            ObjectOutputStream objectOut = new ObjectOutputStream(fileOut);

            objectOut.writeObject(getData());

            objectOut.close();
            fileOut.close();
        } catch (IOException e) {
            e.printStackTrace();
        }
    }

    private void loadData() {
        try {
            // If the data file exists...
            if (new File(Data.DATA_FILE).exists()) {
                // Open the file
                FileInputStream fileIn = new FileInputStream(Data.DATA_FILE);
                ObjectInputStream objectIn = new ObjectInputStream(fileIn);

                data = (Data) objectIn.readObject(); // Read the data in

                // Close the file
                objectIn.close();
                fileIn.close();
            }
        } catch (IOException | ClassNotFoundException e) {
            e.printStackTrace();
        }
    }
}
