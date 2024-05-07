from enum import Enum

class CameraPosition(Enum):
    Null = 0
    Front = 1
    Rear  = 2

# AI - Lift Inspection - Door Status
class LiftDoorStatus(Enum):
    Unknown = -1
    FullyClose = 0
    FullyOpen = 1
    Operating  = 2
    OperatingCloseDoor = 3
    OperatingOpenDoor = 4
    OperatingUnknown = 5

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

class InspectionDataType(Enum):
    # Lift Inspection
    Audio = 1
    VideoFront = 2
    VideoRear = 3
    Preprocess = 4
    Temp = 5
    # Water Leakage
    RGBImage = 6
    ThermalImage = 7
    ThermalImageResult = 8
    WaterLeak_VideoRear = 9

class MissionType(Enum):
    NULL            = 1
    IAQ             = 2
    WaterLeakage    = 3
    LiftInspection  = 4
    LiftAcc         = 7
    LiftLevelling   = 8
    Delivery        = 9 

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

'''
Robot
'''
class RobotStatusMode(Enum):
    IDLE = 1
    EXECUTING = 2
    CHARGING = 3
    ESTOP = 4
    ERROR = 5
    MANUAL = 6
    FOLLOWME = 7
    DELIVERY = 8
    INSPECTION = 9
    pass

class RobotMissionStatus(Enum):
    NULL = -1
    IDLE = 1
    EXECUTING = 2
    FINISH = 3
    pass

class TaskStatus(Enum):
    '''
    For each task status
    '''
    NULL = 1
    EXECUTING = 2
    PAUSE = 3
    STOP = 4
    ERROR = 5
    pass

'''
UI
'''
class UIMissionStatus(Enum):
    IDEL = 1
    EXECUTING = 2
    FINISH = 3
    pass

