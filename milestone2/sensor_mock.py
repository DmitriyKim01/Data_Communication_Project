from time import sleep
import numpy as np

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
