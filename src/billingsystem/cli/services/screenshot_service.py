from datetime import datetime
import os
import threading

import pyscreenshot


class ScreenshotService:
    def __init__(self, recording_name: str = "recording1", interval: float = 5.0):
        self.recording_name = recording_name
        self.interval = interval
        self._stop_event = threading.Event()
        self._thread = None

        self.screenshots_path = os.path.join(".", "recordings", recording_name, "screenshots")
        os.makedirs(self.screenshots_path, exist_ok=True)

    def start_recording(self):
        if self._thread and self._thread.is_alive():
            return
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._record_loop, daemon=True)
        self._thread.start()

    def stop_recording(self):
        self._stop_event.set()
        if self._thread:
            self._thread.join()

    def _record_loop(self):
        while not self._stop_event.is_set():
            image = pyscreenshot.grab()

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
            file_path = os.path.join(self.screenshots_path, f"screenshot_{timestamp}.png")
            image.save(file_path)

            self._stop_event.wait(self.interval)

            #todo: instead of waiting - request to backend to analyze this frame and save it to the database
