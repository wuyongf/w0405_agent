import src.top_module.io_module.linear_actuator as LinearActuator
import src.top_module.sensor.laser_distance_module as LaserDistanceSensor


class LiftLevellingModule():
    def __init__(self):
        self.COM_linear_actuator = 'COM4'
        self.COM_laser_distance_left = 'COM5'
        self.COM_laser_distance_right = 'COM7'

        self.linear_actuator = LinearActuator.LinearActuator(self.COM_linear_actuator)
        self.laser_distance = LaserDistanceSensor.LaserDistanceSensor(self.COM_laser_distance_left, self.COM_laser_distance_right)

    def start(self):
        pass
    
if __name__ == "__main__":
    lift_levelling = LiftLevellingModule()
    lift_levelling.laser_distance.data_integration()