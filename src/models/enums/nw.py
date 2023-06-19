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