from enum import Enum


class LinearActuatorStatus(Enum):
    Error = 0
    Idle = 1
    Extend = 2
    Retract = 3
