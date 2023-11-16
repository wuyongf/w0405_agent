from enum import Enum

# AI - NWDB
class AudioType(Enum):
    Ambient = 1
    Door    = 2
    Vocal   = 3

# AI - IPC Data
class InspectionType(Enum):
    LiftInspection = 1
    Surveillance   = 2
    WaterLeakage   = 3

class MissionType(Enum):
    NULL            = 1
    IAQ             = 2
    WaterLeakage    = 3
    LiftVibration   = 4
    LiftDoorNoise   = 5
    LiftDoorDamage  = 6
    LiftAcc         = 7
    LiftLevelling   = 8
    Delivery        = 9
    Basic_GOTO      = 10
    Basic_Remote    = 11 
    Basic_DoorOpening  = 12 

class Protocol(Enum):
    RVMQTT = 1
    RVAPI = 2

# Lift
class LiftPositionType(Enum):
    CurWaitingPos = 0
    CurTransitPos = 1
    TargetWaitingPos = 2
    TargetTransitPos = 3
    TargetOutPos = 4
    LiftMapIn = 5
    LiftMapTransit = 6
    LiftMapOut = 7

# Delivery
class LockerCommand(Enum):
    Null = 0
    Unlock = 1
    Lock_with_Package = 2
    Lock_without_Package = 3

class DeliveryStatus(Enum):
    Null = -1
    Scheduled = 0
    Comeleted = 1
    Failed = 2
    Aborted = 3  
    Cancelled = 4
    Active_ToSender = 5
    Active_WaitForLoading = 6
    Active_ToReceiver = 7
    Active_WaitForUnloading = 8
    Active_BackToSender = 9
    Active_BackToChargingStation = 10

class RobotStatusMode(Enum):
    Init = 1
    Auto = 2
    Executing = 3
    Charging = 4
    Error = 5
    Manual = 6
    FollowME_Unpair = 7
    FollowME_Paired = 8
    pass
