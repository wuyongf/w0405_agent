

class Status:
    def __init__(self, dct):
        self.percentage = dct['battery_percentage']
        self.map_mir_guid = dct['map_id']
        self.position = Position(dct['position'])

class Position:
    def __init__(self, dct):
        self.y = dct['y']
        self.x = dct['x']
        self.orientation = dct['orientation']