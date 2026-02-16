# gcs/ui_bridge.py

import time
import threading
import eel
from .state import GCSState
from .drone import DroneController
from .video import video_loop
from .joystick import joystick_loop

class UIBridge:
    def __init__(self, state: GCSState, drone: DroneController):
        self.state = state
        self.drone = drone

    def start_background_tasks(self):
        threading.Thread(target=self._telemetry_pusher, daemon=True).start()

    def start_video(self):
        threading.Thread(target=video_loop, args=(self.state, self.drone, self.push_frame), daemon=True).start()

    def start_joystick(self):
        threading.Thread(target=joystick_loop, args=(self.state, self.drone, self.push_joystick), daemon=True).start()

    def _telemetry_pusher(self):
        while self.state.running:
            eel.updateTelemetry(self.state.to_dict())
            try:
                eel.updateJoystick(self.state.joystick_dict())
            except Exception:
                pass
            time.sleep(0.15)

    def push_frame(self, data_url: str):
        eel.updateFrame(data_url)

    def push_joystick(self, js_dict):
        eel.updateJoystick(js_dict)


def register_eel_api(ui: UIBridge):
    @eel.expose
    def ui_connect():
        try:
            ui.drone.connect()
            ui.state.set_running(True)

            ui.start_background_tasks()
            ui.start_video()
            ui.start_joystick()

            return {"ok": True}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    @eel.expose
    def ui_disconnect():
        ui.state.set_running(False)
        ui.drone.disconnect()
        return {"ok": True}


    @eel.expose
    def ui_rc(lr, fb, ud, yw):
        try:
            ui.drone.rc(int(lr), int(fb), int(ud), int(yw))
            return {"ok": True}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    @eel.expose
    def ui_takeoff():
        try:
            ui.drone.takeoff()
            return {"ok": True}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    @eel.expose
    def ui_land():
        try:
            ui.drone.land()
            return {"ok": True}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    @eel.expose
    def ui_emergency():
        try:
            ui.drone.emergency()
            return {"ok": True}
        except Exception as e:
            return {"ok": False, "error": str(e)}
