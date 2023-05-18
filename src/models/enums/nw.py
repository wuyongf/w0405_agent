from enum import Enum

class MissionType(Enum):
    NULL             = 1
    IAQ              = 2
    WaterLeakage     = 3
    LiftVibration    = 4
    LiftDoorNoise    = 5
    LiftDoorDamage   = 6
    LiftAcc          = 7
    LiftLevelling    = 8

class Protocol(Enum):
    RVMQTT = 1
    RVAPI = 2