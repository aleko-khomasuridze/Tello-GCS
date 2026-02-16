# gcs/joystick.py

import time
import pygame
from . import config
from .state import GCSState
from .drone import DroneController

def _apply_deadzone(x: float, dz: float) -> float:
    if abs(x) < dz:
        return 0.0
    sign = 1.0 if x >= 0 else -1.0
    x = (abs(x) - dz) / (1.0 - dz)
    return sign * x

def _expo(x: float, expo: float) -> float:
    sign = 1.0 if x >= 0 else -1.0
    return sign * (abs(x) ** expo)

def _to_cmd(x: float, max_cmd: int) -> int:
    x = max(-1.0, min(1.0, x))
    return int(x * max_cmd)

def joystick_loop(state: GCSState, drone: DroneController, push_js_cb=None):
    pygame.init()
    pygame.joystick.init()

    js = None

    def publish_js(name: str, st: str):
        state.set_joystick(name, st)
        if push_js_cb:
            try:
                push_js_cb(state.joystick_dict())
            except Exception:
                pass

    publish_js("No device", "DISCONNECTED")

    takeoff_latch = False
    land_latch = False

    while state.running:
        try:
            pygame.event.pump()

            if js is None or not js.get_init():
                if pygame.joystick.get_count() <= 0:
                    js = None
                    publish_js("No device", "DISCONNECTED")
                    time.sleep(0.5)
                    continue

                js = pygame.joystick.Joystick(0)
                js.init()
                publish_js(js.get_name(), "CONNECTED")

            pygame.event.pump()

            lx = js.get_axis(config.JOY_AXIS_LX)
            ly = js.get_axis(config.JOY_AXIS_LY)
            rx = js.get_axis(config.JOY_AXIS_RX)
            ry = js.get_axis(config.JOY_AXIS_RY)

            # invert Y axes: up = positive
            roll  = lx
            pitch = -ly
            yaw   = rx
            thr   = -ry

            roll  = _expo(_apply_deadzone(roll,  config.JOY_DEADZONE), config.JOY_EXPO)
            pitch = _expo(_apply_deadzone(pitch, config.JOY_DEADZONE), config.JOY_EXPO)
            yaw   = _expo(_apply_deadzone(yaw,   config.JOY_DEADZONE), config.JOY_EXPO)
            thr   = _expo(_apply_deadzone(thr,   config.JOY_DEADZONE), config.JOY_EXPO)

            lr = _to_cmd(roll,  config.JOY_MAX_CMD)
            fb = _to_cmd(pitch, config.JOY_MAX_CMD)
            yw = _to_cmd(yaw,   config.JOY_MAX_CMD)
            ud = _to_cmd(thr,   config.JOY_MAX_CMD)

            # Send RC continuously
            drone.rc(lr, fb, ud, yw)

            # Optional buttons with edge detect
            btn_takeoff = js.get_button(config.JOY_BTN_TAKEOFF) if js.get_numbuttons() > config.JOY_BTN_TAKEOFF else 0
            btn_land    = js.get_button(config.JOY_BTN_LAND)    if js.get_numbuttons() > config.JOY_BTN_LAND else 0

            if btn_takeoff and not takeoff_latch:
                drone.takeoff()
                takeoff_latch = True
            if not btn_takeoff:
                takeoff_latch = False

            if btn_land and not land_latch:
                drone.land()
                land_latch = True
            if not btn_land:
                land_latch = False

            publish_js(state.joystick_name, f"LR:{lr} FB:{fb} UD:{ud} YW:{yw}")

            time.sleep(1.0 / config.JOY_RATE_HZ)

        except Exception:
            # neutralize if errors/unplug
            try:
                drone.rc(0, 0, 0, 0)
            except Exception:
                pass
            js = None
            publish_js(state.joystick_name, "RECONNECTING")
            time.sleep(0.5)
