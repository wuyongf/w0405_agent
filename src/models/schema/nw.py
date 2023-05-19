import json
import uuid

class Status:
    def __init__(self, battery, position, map_id):
        self.battery = battery
        self.position = position
        self.map_id = map_id
    def to_json(self):
        return json.dumps(self.__dict__, default=lambda o: o.__dict__)
    
class Position:
    def __init__(self, x, y, theta):
        self.x = x
        self.y = y
        self.theta = theta
    def to_json(self):
        return json.dumps(self.__dict__, default=lambda o: o.__dict__)