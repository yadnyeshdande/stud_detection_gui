import serial
import time

# Set up the serial communication parameters
# Replace 'COM_PORT' with the actual COM port where your USB-to-Relay module is connected
# For Linux, it might be something like '/dev/ttyUSB0', '/dev/ttyACM0', etc.
# For Windows, it'll be like 'COM3', 'COM4', etc.
COM_PORT = 'COM4'  # Update with your COM port
BAUD_RATE = 9600  # The baud rate (adjust if needed)

# Define the relay control commands (these depend on your specific relay module)
RELAY_ON = b'1'  # Command to turn relay ON (usually '1', adjust as per your module)
RELAY_OFF = b'0'  # Command to turn relay OFF (usually '0', adjust as per your module)


# Function to control the relay
def control_relay(state):
    try:
        # Initialize the serial connection
        with serial.Serial(COM_PORT, BAUD_RATE, timeout=1) as ser:
            if state == "on":
                print("Turning relay ON")
                ser.write(RELAY_ON)  # Send command to turn relay ON
            elif state == "off":
                print("Turning relay OFF")
                ser.write(RELAY_OFF)  # Send command to turn relay OFF
            else:
                print("Invalid state! Use 'on' or 'off'.")
            time.sleep(1)  # Delay to allow for action to take place

    except serial.SerialException as e:
        print(f"Error connecting to relay module: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")


# Example usage
if __name__ == "__main__":
    while True:
        user_input = input("Enter 'on' to turn on the relay, 'off' to turn it off, or 'exit' to quit: ").strip().lower()

        if user_input == "on":
            control_relay("on")
        elif user_input == "off":
            control_relay("off")
        elif user_input == "exit":
            print("Exiting program.")
            break
        else:
            print("Invalid input. Please type 'on', 'off', or 'exit'.")

"""
import serial

# Replace with the correct COM port from your system
COM_PORT = 'COM4'  # Windows example
# COM_PORT = '/dev/ttyUSB0'  # Linux/macOS example

try:
    # Attempt to open the serial port
    ser = serial.Serial(COM_PORT, 9600, timeout=1)
    print(f"Successfully connected to {COM_PORT}")
    ser.close()
except serial.SerialException as e:
    print(f"Failed to connect to {COM_PORT}: {e}")
"""