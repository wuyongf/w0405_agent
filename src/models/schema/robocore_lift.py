import json
from src.utils import get_unix_timestamp

class State:
    def __init__(self, timestamp, error_code, Lift_Floor, Button_Bitmap):
        self.timestamp = timestamp
        self.error_code = error_code
        self.Lift_Floor = Lift_Floor
        self.Button_Bitmap = Button_Bitmap

    def to_json(self):
        return json.dumps(self.__dict__, default=lambda o: o.__dict__)
    
class Message:
    def __init__(self, timestamp, Press_Time = None, error_code = 0, Key_Press = []):
        self.timestamp = timestamp
        if(Press_Time is not None): self.Press_Time = Press_Time
        self.error_code = error_code
        self.Key_Press = Key_Press

    def to_json(self):
        return json.dumps(self.__dict__, default=lambda o: o.__dict__)