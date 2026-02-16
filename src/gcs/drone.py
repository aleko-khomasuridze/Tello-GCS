# gcs/drone.py

import time
import tellopy
from typing import Optional
from .state import GCSState

class DroneController:
    def __init__(self, state: GCSState):
        self.state = state
        self.tello: Optional[tellopy.Tello] = None

    def connect(self):
        if self.tello:
            return

        self.tello = tellopy.Tello()
        self.tello.subscribe(self.tello.EVENT_FLIGHT_DATA, self._on_flight_data)

        self.tello.connect()
        self.tello.wait_for_connection(60.0)
        self.tello.start_video()

        self.state.set_connected(True)

    def disconnect(self):
        self.state.set_connected(False)
        if not self.tello:
            return
        try:
            self.tello.land()
            time.sleep(0.5)
        except Exception:
            pass
        try:
            self.tello.quit()
        except Exception:
            pass
        self.tello = None

    def takeoff(self):
        if self.tello:
            self.tello.takeoff()

    def land(self):
        if self.tello:
            self.tello.land()

    def emergency(self):
        if self.tello:
            self.tello.emergency()

    def rc(self, lr: int, fb: int, ud: int, yaw: int):
        if not self.tello:
            return
        self.tello.set_roll(lr)
        self.tello.set_pitch(fb)
        self.tello.set_throttle(ud)
        self.tello.set_yaw(yaw)

    def get_video_stream(self):
        if not self.tello:
            return None
        return self.tello.get_video_stream()

    def _on_flight_data(self, event, sender, data):
        try:
            self.state.set_connected(True)

            payload = {}

            if hasattr(data, "battery_percentage"):
                payload["battery"] = int(data.battery_percentage)
            if hasattr(data, "height"):
                payload["height_cm"] = int(data.height)
            if hasattr(data, "fly_time"):
                payload["flight_time_s"] = int(data.fly_time)

            for k in ("speed_x", "speed_y", "speed_z", "wifi_strength"):
                if hasattr(data, k):
                    try:
                        payload[k] = int(getattr(data, k))
                    except Exception:
                        payload[k] = getattr(data, k)

            if hasattr(data, "temperature_low"):
                payload["temp_low"] = int(data.temperature_low)
            if hasattr(data, "temperature_high"):
                payload["temp_high"] = int(data.temperature_high)

            self.state.set_telemetry(**payload)

        except Exception:
            pass
