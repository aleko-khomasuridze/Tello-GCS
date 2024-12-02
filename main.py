import cv2
import pygame
import threading
from djitellopy import Tello

# Initialize Pygame for keyboard handling
pygame.init()
win = pygame.display.set_mode((400, 300))

# Initialize the Tello drone
tello = Tello()
tello.connect()
print(f'Battery: {tello.get_battery()}%')

tello.streamon()
frame_read = tello.get_frame_read()

def video_feed():
    while True:
        cv2.imshow("Tello Video", frame_read.frame)
        cv2.waitKey(1)

def control_tello():
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    tello.land()
                    running = False
                elif event.key == pygame.K_UP:
                    tello.move_up(30)
                elif event.key == pygame.K_DOWN:
                    tello.move_down(30)
                elif event.key == pygame.K_LEFT:
                    tello.move_left(30)
                elif event.key == pygame.K_RIGHT:
                    tello.move_right(30)
                elif event.key == pygame.K_w:
                    tello.move_forward(30)
                elif event.key == pygame.K_s:
                    tello.move_backward(30)
                elif event.key == pygame.K_a:
                    tello.rotate_counter_clockwise(30)
                elif event.key == pygame.K_d:
                    tello.rotate_clockwise(30)
                elif event.key == pygame.K_SPACE:
                    tello.takeoff()
                elif event.key == pygame.K_RETURN:
                    tello.land()

        pygame.time.wait(100)

# Threads for video feed and control handling
video_thread = threading.Thread(target=video_feed)
control_thread = threading.Thread(target=control_tello)

video_thread.start()
control_thread.start()

control_thread.join()
video_thread.join()

cv2.destroyAllWindows()
