import eel
from src.gcs import config
from src.gcs.state import GCSState
from src.gcs.drone import DroneController
from src.gcs.ui_bridge import UIBridge, register_eel_api

def main():
    state = GCSState()
    drone = DroneController(state)
    ui = UIBridge(state, drone)

    eel.init(config.WEB_DIR)
    register_eel_api(ui)

    # Start UI; connect happens from button
    eel.start("index.html", size=(1280, 800), port=0)

if __name__ == "__main__":
    main()
