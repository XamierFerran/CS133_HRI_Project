import pygame
import time
import math
from spherov2 import scanner
from spherov2.sphero_edu import SpheroEduAPI
from spherov2.types import Color

DEAD_ZONE = 0.2  # Dead zone to ignore minor joystick drift

# def connect_sphero():
#     toy = scanner.find_toy(timeout=10)
#     if toy:
#         print(f"Connected to Sphero with address: {toy.address}")
#         time.sleep(2)  # Allow Bluetooth connection to stabilize
#         return toy
#     else:
#         print("No Sphero detected. Make sure it is powered on and in range.")
#         return None

# Address of the specific Sphero device
SPHERO_ADDRESS = "C7:71:F7:8C:33:E3"

def connect_sphero(address=SPHERO_ADDRESS, timeout=10):
    toys = scanner.find_toys(timeout=timeout)  # Scan for all available toys within range
    for toy in toys:
        if toy.address == address:
            print(f"Connected to Sphero with address: {toy.address}")
            time.sleep(2)  # Allow Bluetooth connection to stabilize
            return toy
    print(f"Sphero with address {address} not detected. Make sure it is powered on and in range.")
    return None

def connect_xbox_controller():
    pygame.init()
    pygame.joystick.init()

    if pygame.joystick.get_count() > 0:
        controller = pygame.joystick.Joystick(0)
        controller.init()
        print(f"Connected to Xbox Controller: {controller.get_name()}")
        return controller
    else:
        print("No Xbox Controller detected. Please connect your controller.")
        return None

def calculate_angle(x, y):
    # Invert the X-axis by multiplying by -1 to fix left-right inversion, and adjust by -90 degrees
    angle = (math.degrees(math.atan2(-y, -x)) - 90) % 360
    return angle

def control_sphero(controller, droid):
    running = True
    calibrated_forward = None  # Store the locked forward direction
    calibration_mode = True    # Track if we are in calibration mode

    while running:
        pygame.event.pump()  # Update events

        # Get joystick axes for control
        right_x_axis = controller.get_axis(2)  # Right stick X for rotation
        right_y_axis = controller.get_axis(3)  # Right stick Y for forward calibration
        left_x_axis = controller.get_axis(0)   # Left stick X for orientation
        left_y_axis = controller.get_axis(1)   # Left stick Y for orientation
        right_trigger = controller.get_axis(5) # Right trigger for speed control

        # Calculate angle of the left joystick for orientation
        if abs(left_x_axis) > DEAD_ZONE or abs(left_y_axis) > DEAD_ZONE:
            joystick_angle = calculate_angle(left_x_axis, left_y_axis)
            print(f"Left Joystick - X: {left_x_axis:.2f}, Y: {left_y_axis:.2f}, Angle: {joystick_angle:.2f}°")

            if calibration_mode:
                # Rotate Sphero to the joystick's indicated direction during calibration
                droid.set_heading(int(joystick_angle) % 360)
                print(f"Calibrating... rotating to {int(joystick_angle) % 360} degrees")

        # Button handling
        for event in pygame.event.get():
            if event.type == pygame.JOYBUTTONDOWN:
                if controller.get_button(0):  # 'A' button to lock forward direction
                    if calibration_mode:
                        calibrated_forward = droid.get_heading()
                        calibration_mode = False  # Exit calibration mode
                        print(f"Forward direction locked at {calibrated_forward} degrees")

                elif controller.get_button(1):  # 'B' button to quit
                    print("Exit control loop.")
                    running = False

        # Post-calibration: Use left joystick for orientation and right trigger for speed control
        if not calibration_mode:
            if abs(left_x_axis) > DEAD_ZONE or abs(left_y_axis) > DEAD_ZONE:
                # Adjust orientation based on left joystick direction
                movement_angle = (calibrated_forward + calculate_angle(left_x_axis, left_y_axis)) % 360
                droid.set_heading(int(movement_angle))
                print(f"Orientation set to {int(movement_angle)} degrees")

            # Speed control using right trigger (only positive values)
            if right_trigger > 0:  # Ignore if trigger is not pressed or is negative
                speed = int((right_trigger + 1) * 50)  # Convert trigger range (-1 to 1) to speed (0 to 100)
                droid.set_speed(speed)
                print(f"Moving with speed {speed}")
            else:
                droid.set_speed(0)  # Stop movement if the trigger is released

        time.sleep(0.1)

# Run connection functions
toy = connect_sphero()
controller = connect_xbox_controller()

if toy and controller:
    with SpheroEduAPI(toy) as droid:
        droid.set_main_led(Color(r=0, g=0, b=255))  # Set Sphero main LED to blue
        droid.set_front_led(Color(r=0, g=0, b=255))  # Set front LED to blue
        print("Set Sphero main LED to blue and front LED to white.")
        
        control_sphero(controller, droid)
