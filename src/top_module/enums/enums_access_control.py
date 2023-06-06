from enum import Enum

class DoorStatus(Enum):
    Idle = 0
    Executing = 1
    Finish = 2
    Error = 3
