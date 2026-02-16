# gcs/video.py

import time
import base64
import av
import cv2
from . import config
from .hud import draw_hud
from .state import GCSState
from .drone import DroneController

def video_loop(state: GCSState, drone: DroneController, push_frame_cb):
    """
    push_frame_cb(data_url: str) -> None
    """
    stream = None
    container = None

    # ---- WAIT FOR VALID VIDEO STREAM ----
    for attempt in range(10):
        try:
            stream = drone.get_video_stream()
            if stream is None:
                time.sleep(0.3)
                continue

            # IMPORTANT: small delay lets buffer fill
            time.sleep(0.5)

            container = av.open(stream)
            break

        except av.error.InvalidDataError:
            print("Video not ready yet, retrying...")
            time.sleep(0.5)

    if container is None:
        print("Failed to open video stream.")
        return


    container = av.open(stream)
    last_frame_time = 0.0

    try:
        for frame in container.decode(video=0):
            if not state.running:
                break

            now = time.time()
            if now - last_frame_time < (1.0 / config.FPS_LIMIT):
                continue
            last_frame_time = now

            img = frame.to_ndarray(format="bgr24")
            img = cv2.resize(img, (config.FRAME_W, config.FRAME_H), interpolation=cv2.INTER_AREA)

            img = draw_hud(img, state)

            ok, jpg = cv2.imencode(".jpg", img, [int(cv2.IMWRITE_JPEG_QUALITY), config.JPEG_QUALITY])
            if not ok:
                continue

            b64 = base64.b64encode(jpg.tobytes()).decode("ascii")
            push_frame_cb("data:image/jpeg;base64," + b64)

    except av.error.AVError:
        print("Decoder restart...")
    except Exception as e:
        print("Video loop error:", e)
