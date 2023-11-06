from enum import Enum

class TaskStatusType(Enum):
    Executing = 1
    Completed = 2
    Failed = 3
    Cancelled = 4

class MissionStatus(Enum):
    Completed = 1
    Aborted = 2
    Paused = 3
    Scheduled = 4
    Activated = 5
    Failed = 6