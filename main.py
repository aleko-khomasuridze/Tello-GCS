import cv2
import pygame
import threading
from djitellopy import Tello

# Initialize Pygame and set up the display
pygame.init()
win = pygame.display.set_mode((400, 300))

# Initialize the joystick
pygame.joystick.init()
joystick_count = pygame.joystick.get_count()
if joystick_count == 0:
    print("No joystick detected")
else:
    joystick = pygame.joystick.Joystick(0)
    joystick.init()

# Initialize and connect to the Tello drone
tello = Tello()
tello.connect()
tello.streamon()
print(f'Battery: {tello.get_battery()}%')

# Start the drone's flight
tello.takeoff()

# Video feed function to display the drone's camera output
def video_feed():
    while True:
        frame_read = tello.get_frame_read()
        frame = frame_read.frame
        if frame is not None:
            cv2.putText(frame, f'Battery: {tello.get_battery()}%', (5, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            cv2.imshow("Tello Video", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):  # Press 'q' to quit
                break
    cv2.destroyAllWindows()

# Function to handle drone controls using joystick input
def handle_input():
    running = True
    while running:
        pygame.event.pump()  # Process event queue

        # Read joystick axes and buttons
        yv = int(joystick.get_axis(0) * 60)  # Yaw: Axis 0
        ud = int(joystick.get_axis(1) * -60)  # Up/Down: Axis 1
        lr = int(joystick.get_axis(2) * 60)  # Left/Right: Axis 2
        fb = int(joystick.get_axis(4) * -60)  # Forward/Back: Axis 4

        # Read joystick buttons
        if joystick.get_button(5):  # Button 5: Takeoff
            tello.takeoff()
        if joystick.get_button(4):  # Button 4: Land
            tello.land()
        
        # Send composite movement commands
        tello.send_rc_control(lr, fb, ud, yv)

        pygame.time.delay(10)  # Keep delay short for responsiveness

        # Handle quit event
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                tello.land()

# Handle drone control in the main thread
video_feed()

# Start the video feed in a separate thread
video_thread = threading.Thread(target=handle_input, daemon=True)
video_thread.start()

# Ensure the video thread is terminated
video_thread.join()
