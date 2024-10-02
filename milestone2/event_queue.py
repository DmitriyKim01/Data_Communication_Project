import time
import threading

class EventQueue:
    def __init__(self):
        self.events = []  
        self.timestamps = [] 
        self.event_id_name_map = {
            0: "Deer Grazing",
            1: "Squirrel Running",
            2: "Bear Sleeping",
            3: "Raccoon Scavenging",
            4: "Bird Gathering"
        }
        self.execute_lock = threading.Lock() 
        self.get_lock = threading.Semaphore(len(self.events))

    def add_event(self, id):
        if id not in self.event_id_name_map:
            print(f"Invalid event ID: {id}")
            raise Exception(f"Invalid event ID: {id}")

        with self.execute_lock: 
            current_time = time.time()
            self.events.append(self.event_id_name_map[id]) 
            self.timestamps.append(current_time) 
            self.get_lock.release()
            print(f'Event added: {id} - {self.event_id_name_map[id]}')
            print(f'Timestamp added: {current_time}')

    def get_event(self):
          self.get_lock.acquire()
          with self.execute_lock:
            print('Event happened!')
            return self.events.pop()


