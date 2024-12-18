''' 
To open virtual environment:
python3 -m venv spherov2-env
source spherov2-env/bin/activate
pip install spherov2
./spherov2-env/bin/python spheroOption.py
'''

import math, time 
from spherov2 import scanner
from spherov2.sphero_edu import SpheroEduAPI
from spherov2.types import Color

# Controller and Bot Sphero addresses 
# Addresses assume format xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx where x is a number or capital letter
SPHERO_ADDRESS_1 = ""
SPHERO_ADDRESS_2 = ""
step = 0.1
K = 1	# Proportional controller gain 

# Kalman filter variables for pitch
x = 0.0  # State (pitch angle)
P = 1.0  # Error covariance
Q = 0.08  # Process noise
R = 0.2   # Measurement noise

def kalman_filter(angle, gyro_rate, dt, x, P, Q, R):
	# Prediction step
	x_pred = x + gyro_rate * dt  # Predicted state estimate
	P_pred = P + Q               # Predicted error covariance

	# Measurement update step
	K = P_pred / (P_pred + R)      # Kalman gain
	x = x_pred + K * (angle - x_pred)  # Updated state estimate
	P = (1 - K) * P_pred           # Updated error covariance

	return x

def connect_sphero(address, timeout=10):
	toys = scanner.find_toys(timeout=timeout)
	for toy in toys:
		if toy.address == address:
			print(f"Connected to Sphero with address: {toy.address}")
			time.sleep(2)  # Allow Bluetooth connection to stabilize
			return toy
	print(f"Sphero with address {address} not detected. Make sure it is powered on and in range.")
	return None

def read_imu_data(control,bot):
	direction = 0
	try:
		while True:
			# Read IMU data
			accel = control.get_acceleration()
			gyro = control.get_gyroscope()

			# Compute angles
			accel_angle_pitch = math.atan2(accel['y'], math.sqrt(accel['x']**2 + accel['z']**2)) * 180 / math.pi
			accel_angle_roll = math.atan2(accel['x'], math.sqrt(accel['y']**2 + accel['z']**2)) * 180 / math.pi
			gyro_rate_pitch = gyro['x']  # Angular velocity in degrees/s
			gyro_rate_roll = gyro['y']   # Angular velocity in degrees/s for roll
		

			# Apply Kalman filter
			pitch = kalman_filter(accel_angle_pitch, gyro_rate_pitch, step, x, P, Q, R)
			roll = kalman_filter(accel_angle_roll, gyro_rate_roll, step, x, P, Q, R)

			[dominant,xy] = find_dominant(pitch,roll)
			speed = map_to_speed(dominant)
			if speed: 
				direction = map_to_direction(dominant,xy)
			
			
			bot.set_heading(direction)
			bot.set_speed(speed)

			print(f"Pitch: {pitch:.2f}, Roll: {roll:.2f}")
			time.sleep(step)

	except KeyboardInterrupt:
		print("Stopped IMU data reading.")
	except Exception as e:
		print(f"Error during IMU data read: {e}")

def find_dominant(pitch,roll):
	if abs(pitch) >= abs(roll):
		dominant = pitch
		xy = 0
		print(f"Pitch: {dominant}")
	else:
		dominant = roll
		xy = 1
		print(f"Roll: {dominant}")
	return dominant, xy

def map_to_direction(dominant,xy):
	if xy == 0:
		if dominant >= 0:
			direction = 0
		else:
			direction = 180
	elif xy == 1:
		if dominant >= 0:
			direction = 90
		else:
			direction = 270
	else: 
		print("Invalid inputs to map_to_direction()")
	return direction

def map_to_speed(dominant):
	if dominant >= 10:
		speed = int(dominant * K)
	elif dominant >= -10:
		speed = 0
	else:
		speed = int(dominant * K)
	
	return int(speed)

# Connect to the Sphero
control = connect_sphero(SPHERO_ADDRESS_1)
bot = connect_sphero(SPHERO_ADDRESS_2)

# If connection is successful, start reading IMU data
if control and bot:
	with SpheroEduAPI(control) as control, SpheroEduAPI(bot) as bot:
		control.set_main_led(Color(r=0, g=255, b=0))  
		control.set_stabilization(False)
		print("Connected to control Sphero and set LED to green.")
		
		bot.set_main_led(Color(r=0, g=0, b=255))
		print("Connected to moving Sphero and set LED to blue.")
   	 
		# Start reading and printing IMU data
		read_imu_data(control,bot)
else:
	print("Failed to connect to the Sphero.")

