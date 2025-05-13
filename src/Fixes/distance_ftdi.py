"""import serial
import time

# Initialize serial communication (adjust the COM port as needed)
ser = serial.Serial('COM4', 9600, timeout=1)  # Update this with your FT232RL COM port

# HC-SR04 pin configuration
TRIG_PIN = 23  # GPIO pin connected to Trig
ECHO_PIN = 24  # GPIO pin connected to Echo


# Initialize GPIO (if using Raspberry Pi, or GPIO simulation)
# GPIO.setmode(GPIO.BCM)  # Uncomment this for actual Raspberry Pi usage
# GPIO.setup(TRIG_PIN, GPIO.OUT)
# GPIO.setup(ECHO_PIN, GPIO.IN)

def measure_distance():
    # Send a pulse to the TRIG pin
    ser.write(b'1')  # Send a signal to trigger (assuming your setup is receiving data here)

    # Trigger the HC-SR04 sensor
    # GPIO.output(TRIG_PIN, GPIO.HIGH)
    # time.sleep(0.00001)  # 10 microseconds pulse
    # GPIO.output(TRIG_PIN, GPIO.LOW)

    # Wait for the Echo pin to go HIGH (pulse returned)
    # pulse_start = time.time()
    # while GPIO.input(ECHO_PIN) == 0:
    #     pulse_start = time.time()

    # pulse_end = time.time()
    # while GPIO.input(ECHO_PIN) == 1:
    #     pulse_end = time.time()

    # Calculate distance
    # pulse_duration = pulse_end - pulse_start
    # distance = pulse_duration * 17150  # Speed of sound = 343 m/s, distance in cm
    # distance = round(distance, 2)

    # Simulating distance reading
    distance = 25.0  # Simulated distance for testing (in cm)

    # Send the distance back via serial port
    ser.write(f'Distance: {distance} cm\n'.encode())

    return distance


def main():
    try:
        while True:
            distance = measure_distance()
            print(f"Measured Distance: {distance} cm")
            time.sleep(1)  # Measure every second
    except KeyboardInterrupt:
        print("Program interrupted")
    finally:
        ser.close()


if __name__ == "__main__":
    main()
"""


import serial

try:
    ser = serial.Serial('COM4', 9600, timeout=1)
    print("Monitoring IR sensor signal on COM4...")

    while True:
        data = ser.read(1)  # read 1 byte at a time
        if data:
            print(f"Signal: {data.hex()}")

except serial.SerialException as e:
    print(f"Serial error: {e}")
except KeyboardInterrupt:
    print("Stopped.")
finally:
    if 'ser' in locals():
        ser.close()
import serial

try:
    ser = serial.Serial('COM4', 9600, timeout=1)
    print("Monitoring IR sensor signal on COM4...")

    while True:
        data = ser.read(1)  # read 1 byte at a time
        if data:
            print(f"Signal: {data.hex()}")

except serial.SerialException as e:
    print(f"Serial error: {e}")
except KeyboardInterrupt:
    print("Stopped.")
finally:
    if 'ser' in locals():
        ser.close()
