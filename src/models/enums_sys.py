from enum import Enum

class Model(Enum):
    RM = 1
    RV = 2
    NWDB = 3

class RMTaskStatusType(Enum):
    Executing = 1
    Complete = 2
    Fail = 3