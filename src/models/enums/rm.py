from enum import Enum

class TaskStatusType(Enum):
    Executing = 1
    Complete = 2
    Fail = 3

class MissionStatus(Enum):
    Completed = 1
    Aborted = 2
    Paused = 3
    Scheduled = 4
    Activated = 5