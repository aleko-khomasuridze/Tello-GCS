# gcs/config.py

WEB_DIR = "web"

# Video
FRAME_W = 960
FRAME_H = 720
JPEG_QUALITY = 75
FPS_LIMIT = 30

# Joystick
JOY_DEADZONE = 0.08
JOY_RATE_HZ = 30
JOY_EXPO = 1.6
JOY_MAX_CMD = 70

# Axis mapping (change if your controller differs)
JOY_AXIS_LX = 0
JOY_AXIS_LY = 1
JOY_AXIS_RX = 2
JOY_AXIS_RY = 3

# Buttons (optional)
JOY_BTN_TAKEOFF = 4  # L1 often
JOY_BTN_LAND = 5     # R1 often
