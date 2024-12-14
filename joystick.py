import pygame
import tkinter as tk
from tkinter import StringVar

# Initialize Pygame
pygame.init()
pygame.joystick.init()

class JoystickApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Joystick Data Viewer")

        # Attempt to initialize the joystick
        if pygame.joystick.get_count() > 0:
            self.joystick = pygame.joystick.Joystick(0)
            self.joystick.init()
            joystick_name = self.joystick.get_name()
        else:
            joystick_name = "No joystick found"

        # UI elements
        self.label_joystick_name = tk.Label(master, text=f"Joystick: {joystick_name}")
        self.label_joystick_name.pack()

        self.axis_vars = [StringVar() for _ in range(self.joystick.get_numaxes())]
        self.axis_labels = [tk.Label(master, textvariable=var) for var in self.axis_vars]
        for label in self.axis_labels:
            label.pack()

        self.button_vars = [StringVar() for _ in range(self.joystick.get_numbuttons())]
        self.button_labels = [tk.Label(master, textvariable=var) for var in self.button_vars]
        for label in self.button_labels:
            label.pack()

        self.hat_vars = [StringVar() for _ in range(self.joystick.get_numhats())]
        self.hat_labels = [tk.Label(master, textvariable=var) for var in self.hat_vars]
        for label in self.hat_labels:
            label.pack()

        # Update the GUI with joystick data
        self.update_joystick()

    def update_joystick(self):
        pygame.event.pump()  # Process event queue

        # Update axes
        for i, var in enumerate(self.axis_vars):
            axis_value = self.joystick.get_axis(i)
            var.set(f"Axis {i}: {axis_value:.2f}")

        # Update buttons
        for i, var in enumerate(self.button_vars):
            button_state = self.joystick.get_button(i)
            var.set(f"Button {i}: {button_state}")

        # Update hats
        for i, var in enumerate(self.hat_vars):
            hat_state = self.joystick.get_hat(i)
            var.set(f"Hat {i}: {hat_state}")

        # Schedule the next update
        self.master.after(100, self.update_joystick)

def main():
    root = tk.Tk()
    app = JoystickApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
