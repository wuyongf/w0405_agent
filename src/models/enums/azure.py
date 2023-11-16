from enum import Enum

class ContainerName(Enum):
    LiftInspection_Audio        = 0
    LiftInspection_VideoFront   = 1
    LiftInspection_VideoRear    = 2
    WaterLeakage_Thermal        = 3
    WaterLeakage_VideoRear      = 4
    Surveillance_Audio          = 5
    Surveillance_VideoFront     = 6
    Surveillance_VideoRear      = 7
    Surveillance_Thermal        = 8