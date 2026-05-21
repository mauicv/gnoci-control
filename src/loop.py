import threading
import time

class Loop:
    def __init__(self, hz, func):
        self.interval = 1.0 / hz
        self.func = func
        self._running = False
        self._thread = None

    def start(self):
        self._running = True
        self._thread = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()

    def _loop(self):
        next_tick = time.perf_counter()
        while self._running:
            self.func()
            next_tick += self.interval
            sleep_time = next_tick - time.perf_counter()
            if sleep_time > 0:
                time.sleep(sleep_time)

    def stop(self):
        self._running = False
        if self._thread:
            self._thread.join()