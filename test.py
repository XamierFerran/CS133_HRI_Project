import time
from spherov2 import scanner
from spherov2.sphero_edu import SpheroEduAPI
from spherov2.types import Color

def connect_sphero(timeout=10):
	toy = scanner.find_toy(timeout=timeout)
	if toy:
    	print(f"Connected to Sphero with address: {toy.address}")
    	time.sleep(2)  # Allow Bluetooth connection to stabilize
    	return toy
	else:
    	print("No Sphero detected. Make sure it is powered on and in range.")
    	return None

def read_imu_data(droid):
	try:
    	while True:
        	# Get accelerometer and gyro data
        	accel = droid.get_acceleration()  # Get acceleration data as a dictionary
        	gyro = droid.get_gyroscope()  	# Get gyroscope data as a dictionary

        	# Display IMU readings in a consistent format
        	print(f"Accel - X: {accel['x']:.3f}, Y: {accel['y']:.3f}, Z: {accel['z']:.3f}")
        	print(f"Gyro - X: {gyro['x']:.3f}, Y: {gyro['y']:.3f}, Z: {gyro['z']:.3f}")

        	time.sleep(0.1)  # Adjust the sleep time to control update rate
	except KeyboardInterrupt:
    	print("Stopped IMU data reading.")
	except Exception as e:
    	print(f"Error during IMU data read: {e}")

# Connect to the Sphero
toy = connect_sphero()

# If connection is successful, start reading IMU data
if toy:
	with SpheroEduAPI(toy) as droid:
    	droid.set_main_led(Color(r=0, g=255, b=0))  # Set Sphero LED to green to indicate a successful connection
    	print("Connected to Sphero and set LED to green.")
   	 
    	# Start reading and printing IMU data
    	read_imu_data(droid)
else:
	print("Failed to connect to the Sphero.")
