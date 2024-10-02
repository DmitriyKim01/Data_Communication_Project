from time import sleep
import numpy as np
from pynput.keyboard import Key, Listener

class MockSensor():
    def __init__(self):
        self.done=False

    def create_events(self, queue):
        rng = np.random.default_rng()
        ids = list(queue.event_id_name_map.keys())
        mean_timeout=5
        min_timeout=1
        while not self.done:
            id = rng.choice(ids)
            queue.add_event(id)
            #timeout is a clipped normal distribution, to ensure a minimum timeout
            timeout = max((rng.normal(mean_timeout)), min_timeout)
            sleep(timeout)

    def stop(self):
        self.done=True

class MotionSensor():
    def __init__(self, pin):
        self.pin = pin
        self.motion_detected = 0
        self.when_motion = None
        self.when_no_motion = None

    def on_press(self,key):
        self.motion_detected = 1

    def on_release(self,key):
        self.motion_detected = 0
        if key == Key.esc:
            return False

    def keyboard_loop(self):
        with Listener(on_press=self.on_press,
                      on_release=self.on_release) as listener:
            listener.join()


    def wait_for_no_motion(self):
        while self.motion_detected == 1:
            sleep(0.1)
        return

    def wait_for_motion(self):
        while self.motion_detected == 0:
            sleep(0.1)
        return
