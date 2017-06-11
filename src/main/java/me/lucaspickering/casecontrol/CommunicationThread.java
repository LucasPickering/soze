package me.lucaspickering.casecontrol;

import java.awt.Color;
import java.io.IOException;
import java.net.DatagramPacket;
import java.net.DatagramSocket;
import java.net.InetAddress;
import java.net.SocketException;
import java.net.UnknownHostException;
import java.nio.ByteBuffer;

public final class CommunicationThread extends Thread {

    private static final int LOOP_TIME = 20;

    private final DatagramSocket socket;
    private final InetAddress clientAddr;
    private final int clientPort;

    private boolean runLoop;

    public CommunicationThread(String clientAddr, int clientPort) {
        try {
            socket = new DatagramSocket();
            this.clientAddr = InetAddress.getByName(clientAddr);
            this.clientPort = clientPort;
        } catch (SocketException | UnknownHostException e) {
            throw new RuntimeException(e);
        }
    }

    @Override
    public void start() {
        runLoop = true;
        super.start();
    }

    public void terminate() {
        runLoop = false;
    }

    @Override
    public void run() {
        while (runLoop) {
            final Data data = CaseControl.data(); // The data to be written

            // Convert the data to bytes and build a packet for it
            final ByteBuffer dataBuffer = convertDataToBytes(data);
            final DatagramPacket packet = new DatagramPacket(
                dataBuffer.array(), dataBuffer.position(), clientAddr, clientPort);

            // Send the packet
            try {
                socket.send(packet);
            } catch (IOException e) {
                System.err.println("Error sending data over socket:");
                e.printStackTrace();
            }

            Funcs.pause(LOOP_TIME); // Pause for a bit
        }

        socket.close(); // Close the socket
    }

    private ByteBuffer convertDataToBytes(Data data) {
        final ByteBuffer buffer = ByteBuffer.allocate(128);
        writeCaseColor(data, buffer);
        writeLcdColor(data, buffer);
        writeLcdText(data, buffer);
        return buffer;
    }

    /**
     * Writes the current case color to the given buffer. The color will be written to the end of
     * the buffer as 3 bytes in RGB format.
     *
     * @param data   the data containing the current case color
     * @param buffer the buffer to write the color to
     */
    private void writeCaseColor(Data data, ByteBuffer buffer) {
        final Color color = data.getCaseColor();
        buffer.put((byte) color.getRed());
        buffer.put((byte) color.getGreen());
        buffer.put((byte) color.getBlue());

    }

    /**
     * Writes the current LCD color to the given buffer. The color will be written to the end of
     * the buffer as 3 bytes in RGB format.
     *
     * @param data   the data containing the current LCD color
     * @param buffer the buffer to write the color to
     */
    private void writeLcdColor(Data data, ByteBuffer buffer) {
        final Color color = data.getLcdColor();
        buffer.put((byte) color.getRed());
        buffer.put((byte) color.getGreen());
        buffer.put((byte) color.getBlue());
    }

    /**
     * Writes the current LCD text to the given buffer.
     *
     * @param data   the data containing the current LCD text
     * @param buffer the buffer to write the text to
     */
    private void writeLcdText(Data data, ByteBuffer buffer) {
        final String joinedStr = String.join("\n", data.getLcdText());
        buffer.put(joinedStr.getBytes());
    }
}
