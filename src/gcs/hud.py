# gcs/hud.py

import cv2
import numpy as np
from .state import GCSState

def draw_hud(frame_bgr: np.ndarray, state: GCSState) -> np.ndarray:
    overlay = frame_bgr.copy()

    batt = state.battery
    h = state.height_cm
    ft = state.flight_time_s

    # Top bar
    cv2.rectangle(overlay, (0, 0), (overlay.shape[1], 48), (18, 18, 22), -1)

    left_txt = f"TELLO GCS  |  BATT: {batt if batt is not None else '--'}%"
    mid_txt  = f"ALT: {h if h is not None else '--'} cm"
    right_txt= f"TIME: {ft if ft is not None else '--'} s"

    cv2.putText(overlay, left_txt, (14, 32), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (230, 230, 240), 2)
    cv2.putText(overlay, mid_txt,  (360, 32), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (230, 230, 240), 2)
    cv2.putText(overlay, right_txt,(720, 32), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (230, 230, 240), 2)

    # Crosshair
    cx, cy = overlay.shape[1] // 2, overlay.shape[0] // 2
    cv2.line(overlay, (cx - 16, cy), (cx + 16, cy), (120, 255, 180), 2)
    cv2.line(overlay, (cx, cy - 16), (cx, cy + 16), (120, 255, 180), 2)

    return overlay
