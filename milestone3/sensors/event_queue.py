import threading
import datetime

class Event:
    def __init__(self, type, time, value):
        self.type = type
        self.time = time
        self.value = value

    def __str__(self):
        return f'{self.type} at {self.time}'
    
class EventQueue:
    def __init__(self):
        self.events = []
        self.execute_lock = threading.Lock() 
        self.get_lock = threading.Semaphore(0)
        
    def add_event(self, event):
        if not isinstance(event, Event):
            raise Exception('Invalid event type')

        with self.execute_lock: 
            current_time = datetime.datetime.now().strftime('%Y-%m-%d_%Hh-%Mm-%Ss')
            self.events.append(event)
            self.get_lock.release()

    def get_event(self):
          self.get_lock.acquire()
          with self.execute_lock:
            event = self.events.pop()
            if not isinstance(event, Event):
                raise Exception('Invalid event type')
            return event

