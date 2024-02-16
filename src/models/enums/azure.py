from enum import Enum

class ContainerName(Enum):
    LiftInspection_Audio        = 0
    LiftInspection_VideoFront   = 1
    LiftInspection_VideoRear    = 2
    WaterLeakage_Thermal        = 3
    WaterLeakage_Thermal_Result = 4
    WaterLeakage_VideoRear      = 5
    WaterLeakage_RGBImage       = 6
    Surveillance_Audio          = 7
    Surveillance_VideoFront     = 8
    Surveillance_VideoRear      = 9
    Surveillance_Thermal        = 10