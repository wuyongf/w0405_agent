from abc import ABC, abstractmethod

class IAQ(ABC):
    @abstractmethod
    def __init__(self, *args, **kwargs):
        """
        Steps:
        1. init class variables
        2. connect the iaq sensor
        """
        pass

    @abstractmethod
    def start(self, *args, **kwargs):
        """
        Starts the IAQ sensor, enables the fan.
        """
        pass

    @abstractmethod
    def enable_task_mode(self, *args, **kwargs):
        """
        Uploads the collected data to a database.
        """
        pass

    @abstractmethod
    def disable_task_mode(self, *args, **kwargs):
        """
        Stop uploading the collected data to a database.
        """
        pass

    @abstractmethod
    def set_mission_id(self, *args, **kwargs):
        """
        set mission_id.
        """
        pass

class LaserDistanceSensor(ABC):
    @abstractmethod
    def __init__(self, *args, **kwargs):
        """
        Steps:
        1. init class variables
        2. connect the laser distance sensor
        """
        pass

    @abstractmethod
    def start_data_collection(self, *args, **kwargs):
        """
        start collecting the data
        """
        pass

    @abstractmethod
    def stop_data_collection(self, *args, **kwargs):
        """
        stop collecting the data. reset linear actuators.
        """
        pass

    @abstractmethod
    def get_height_difference(self, *args, **kwargs):
        pass

    @abstractmethod
    def upload_to_cloud(self, *args, **kwargs):
        pass

class PhoneDevice(ABC):
    @abstractmethod
    def __init__(self, *args, **kwargs):
        """
        Steps:
        1. init class variables
        2. connect the relevant sensors. e.g. ultrasound sensor, motor.
        """
        pass

    @abstractmethod
    def open_door(self, *args, **kwargs):
        """
        start rotating the phone to rotate
        """
        pass

    @abstractmethod
    def is_door_open(self, *args, **kwargs):
        pass

class Locker(ABC):
    @abstractmethod
    def __init__(self, *args, **kwargs):
        """
        Steps:
        1. init class variables
        2. connect the relevant sensors.
        """
        pass

    @abstractmethod
    def is_locker_open(self, *args, **kwargs):
        pass

    @abstractmethod
    def open_locker(self, *args, **kwargs):
        pass

    @abstractmethod
    def upload_to_cloud(self, *args, **kwargs):
        pass

class Monitor(ABC):
    @abstractmethod
    def __init__(self, *args, **kwargs):
        """
        Steps:
        1. init class variables
        2. connect the relevant sensors.
        """
        pass

    @abstractmethod
    def start_face_tracking(self, *args, **kwargs):
        """
        Steps:
        1. Enable some functions to detect human face.
        2. Use control functions to tile the monitor.
        """
        pass

    @abstractmethod
    def stop_face_tracking(self, *args, **kwargs):
        """
        """
        pass

class LiftInspectionSensor(ABC):
    @abstractmethod
    def __init__(self, *args, **kwargs):
        """
        Steps:
        1. init class variables
        2. connect the relevant sensors. e.g. gyro, camera, microphone
        """
        pass

    @abstractmethod
    def collect_gyro_data(self, *args, **kwargs):
        pass

    # Sound Related Methods
    @abstractmethod
    def start_sound_recording(self, *args, **kwargs):
        pass

    @abstractmethod
    def stop_sound_recording(self, *args, **kwargs):
        pass
    
    # Video Related Methods
    @abstractmethod
    def start_video_recording(self, *args, **kwargs):
        pass

    @abstractmethod
    def stop_video_recording(self, *args, **kwargs):
        pass

    @abstractmethod
    def upload_to_cloud(self, *args, **kwargs):
        pass
    

class InternalDevice(ABC):
    @abstractmethod
    def __init__(self, *args, **kwargs):
        """
        Steps:
        1. init class variables
        2. connect the relevant sensors.
        """
        pass

    @abstractmethod
    def get_temperature(self, *args, **kwargs):
        pass

    @abstractmethod
    def get_fan_speed(self, *args, **kwargs):
        pass

    @abstractmethod
    def set_fan_speed(self, *args, **kwargs):
        pass

    @abstractmethod
    def upload_to_cloud(self, *args, **kwargs):
        pass

class ThermalCam(ABC):
    @abstractmethod
    def __init__(self, *args, **kwargs):
        """
        Steps:
        1. init class variables
        2. connect the relevant sensors.
        """
        pass

    @abstractmethod
    def start(self, *args, **kwargs):
        pass

    @abstractmethod
    def stop(self, *args, **kwargs):
        pass

    @abstractmethod
    def check_water_leakage(self, *args, **kwargs):
        pass
    
    @abstractmethod
    def upload_to_cloud(self, *args, **kwargs):
        pass
