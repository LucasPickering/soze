package me.lucaspickering.casecontrol;

import org.apache.commons.cli.CommandLineParser;
import org.apache.commons.cli.DefaultParser;

import java.io.File;
import java.io.FileInputStream;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.ObjectInputStream;
import java.io.ObjectOutputStream;
import java.util.Scanner;

import me.lucaspickering.casecontrol.command.Command;

public final class CaseControl {

	private static final CaseControl caseControl = new CaseControl();
	private static boolean run = true;

	private final ModeThread modeThread = new ModeThread();
	private final SerialThread serialThread = new SerialThread();
	private Data data = new Data();
	private CommandLineParser parser = new DefaultParser();

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
		Runtime.getRuntime().addShutdownHook(serialThread);
		loadData();
		modeThread.start();
		serialThread.start();
		Scanner scanner = new Scanner(System.in);
		do {
			System.out.print(">");
			runInput(scanner.nextLine().toLowerCase());
		} while (run);
		saveData();
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
		Command command = null;
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
