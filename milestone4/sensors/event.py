class Event:
    def __init__(self, type, time, value):
        self.type = type
        self.time = time
        self.value = value

    def __str__(self):
        return f'{self.type} at {self.time}'
    

