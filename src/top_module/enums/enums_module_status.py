from enum import Enum

class LiftLevellingStatus(Enum):
    Idle = 0
    Executing = 1
    Finish = 2
    Error = 3
