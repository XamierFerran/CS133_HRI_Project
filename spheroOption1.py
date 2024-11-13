import time
from spherov2 import scanner
from spherov2.sphero_edu import SpheroEduAPI
from spherov2.types import Color
import math

# Addresses of the two specific Sphero devices
SPHERO_ADDRESS_1 = "CC:90:C0:34:D9:6A"
SPHERO_ADDRESS_2 = "C7:71:F7:8C:33:E3"

# def connect_sphero(address, timeout=10):
#     toys = scanner.find_toys(timeout=timeout)
#     for toy in toys:
#         if toy.address == address:
#             print(f"Connected to Sphero with address: {toy.address}")
#             time.sleep(2)  # Allow Bluetooth connection to stabilize
#             return toy
#     print(f"Sphero with address {address} not detected. Make sure it is powered on and in range.")
#     return None

def connect_sphero(mac_address="C7:71:F7:8C:33:E3"):
    toy = scanner.find_toy(timeout=10, address=mac_address)
    if toy:
        print(f"Connected to Sphero with address: {toy.address}")
        time.sleep(2)  # Allow Bluetooth connection to stabilize
        return toy
    else:
        print(f"No Sphero detected with address {mac_address}. Make sure it is powered on and in range.")
        return None

def read_imu_data(droid, second_droid):
    try:
        while True:
            # Get accelerometer and gyro data from the first Sphero (droid)
            accel = droid.get_acceleration()  # Get acceleration data as a dictionary
            gyro = droid.get_gyroscope()      # Get gyroscope data as a dictionary

            # Map acceleration data to control the second Sphero's speed
            speed = map_to_speed(math.sqrt(accel['x']**2 + accel['y']**2))
            direction = int(math.degrees(math.atan2(accel['y'], accel['x']))) % 360  # Convert to degrees and normalize

            # Print the IMU data for debugging
            print(f"Accel - X: {accel['x']:.3f}, Y: {accel['y']:.3f}, Z: {accel['z']:.3f}")
            print(f"Gyro - X: {gyro['x']:.3f}, Y: {gyro['y']:.3f}, Z: {gyro['z']:.3f}")
            print(f"Mapped Speed: {speed}, Direction: {direction}")

            # Set the speed and direction of the second Sphero with a duration in seconds
            second_droid.roll(speed, direction, 1)  # Roll with specified speed and direction for 1 second

            time.sleep(0.1)  # Adjust the sleep time to control update rate
    except KeyboardInterrupt:
        print("Stopped IMU data reading.")
    except Exception as e:
        print(f"Error during IMU data read: {e}")

def map_to_speed(accel_magnitude):
    # Map the acceleration magnitude (0 to ~1.4 for diagonal max) to a speed range (0 to 255)
    speed = max(0, min(255, int(accel_magnitude * 255)))
    return speed

# Connect to the first Sphero with a specific address
toy1 = connect_sphero(SPHERO_ADDRESS_1)

# Connect to the second Sphero with a specific address
toy2 = connect_sphero(SPHERO_ADDRESS_2)

# If both connections are successful, start reading IMU data and controlling the second Sphero
if toy1 and toy2:
    with SpheroEduAPI(toy1) as droid1, SpheroEduAPI(toy2) as droid2:
        droid1.set_main_led(Color(r=0, g=255, b=0))  # Set the first Sphero's LED to green
        droid2.set_main_led(Color(r=0, g=0, b=255))  # Set the second Sphero's LED to blue
        print("Connected to both Spheros and set LEDs.")

        # Start reading and controlling the second Sphero
        read_imu_data(droid1, droid2)
else:
    print("Failed to connect to one or both Spheros.")
