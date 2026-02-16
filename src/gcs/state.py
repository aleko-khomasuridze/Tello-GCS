# gcs/state.py

from dataclasses import dataclass, field
from typing import Optional, Dict, Any
import threading

@dataclass
class GCSState:
    running: bool = False
    connected: bool = False

    battery: Optional[int] = None
    height_cm: Optional[int] = None
    speed_x: Optional[int] = None
    speed_y: Optional[int] = None
    speed_z: Optional[int] = None
    wifi_strength: Optional[int] = None
    flight_time_s: Optional[int] = None
    temp_low: Optional[int] = None
    temp_high: Optional[int] = None

    joystick_name: str = "No device"
    joystick_state: str = "DISCONNECTED"

    lock: threading.Lock = field(default_factory=threading.Lock)

    def to_dict(self) -> Dict[str, Any]:
        with self.lock:
            return {
                "connected": self.connected,
                "battery": self.battery,
                "height_cm": self.height_cm,
                "speed_x": self.speed_x,
                "speed_y": self.speed_y,
                "speed_z": self.speed_z,
                "wifi_strength": self.wifi_strength,
                "flight_time_s": self.flight_time_s,
                "temp_low": self.temp_low,
                "temp_high": self.temp_high,
            }

    def set_telemetry(self, **kwargs):
        with self.lock:
            for k, v in kwargs.items():
                setattr(self, k, v)

    def set_connected(self, val: bool):
        with self.lock:
            self.connected = val

    def set_running(self, val: bool):
        with self.lock:
            self.running = val

    def set_joystick(self, name: str, state: str):
        with self.lock:
            self.joystick_name = name
            self.joystick_state = state

    def joystick_dict(self) -> Dict[str, Any]:
        with self.lock:
            return {"name": self.joystick_name, "state": self.joystick_state}
