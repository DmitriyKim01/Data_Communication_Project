class EventQueue():
    def __init__(self):
        self.events = []
        self.timestamps = []
        self.event_id_name_map = {0:'Example'} #Replace with your own map

    '''
    Adds events to the event array  and timestamps to the timestamp array
    '''
    def add_event(self,id):
        print(f'add_event: {id} {self.event_id_name_map[id]}')
        pass

    '''
    Pops events from the event array and timestamp array
    If no event available, blocks until one becomes available.
    (i.e. Should always return an event.)
    '''
    def get_event(self):
        return None
