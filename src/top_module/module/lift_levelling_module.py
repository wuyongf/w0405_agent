import threading
import src.top_module.io_module.linear_actuator as LinearActuator
import src.top_module.sensor.distance as LaserDistanceSensor
import src.top_module.analysis.leveling_detection as LevelingDetection
import src.top_module.db_top_module as NWDB
import src.utils.methods as umethods
import src.top_module.enums.enums_linear_actuator as LAEnum
import src.top_module.enums.enums_laser_distance as LDEnum
import src.top_module.enums.enums_module_status as MoEnum
import time


class LiftLevellingModule():
    def __init__(self, modb, config, port_config, status_summary):
        # self.nwdb = NWDB.TopModuleDBHandler(config)
        self.modb = modb
        self.status_summary = status_summary
        self.lld = LevelingDetection.lift_leveling_detection(modb, config, status_summary)
        self.laser_distance = LaserDistanceSensor.LaserDistanceSensor(modb, port_config)
        self.cb_dir = self.callback_direction
        self.cb_finish = self.callback_finish
        self.linear_actuator = LinearActuator.LinearActuator(port_config, self.cb_dir, self.cb_finish)
        self.pack_id = 0
        self.task_id = 0
        self.status = MoEnum.LiftLevellingStatus.Idle
        self.run_flag = 0
        

    def set_task_id(self, id):
        self.task_id = id

    def thread_get_status(self):
        while (True):
            print(self.status)
            time.sleep(1)

    def get_status(self):
        return self.status

    def callback_direction(self):
        # called when linear acturator finish extent
        self.laser_distance.set_retract_flag(True)
        print("callback: change direction")
        time.sleep(1)

        # Callback function when linear actuator finish extent,
        # 1. stop collecting data and upload immediately
        # 2. change move_dir
        # 3. get move_dir
        # 4. collect data again

    def callback_finish(self):
        # called when linear acturator finish retract
        print("callback: finish")
        self.laser_distance.stop()
        self.status = MoEnum.LiftLevellingStatus.Finish
        time.sleep(1)
        self.lld.start_detection(task_id=self.task_id)
        # self.laser_distance.set_move_dir(LAEnum.LinearActuatorStatus.Extend.value)
        self.linear_actuator.stop()

    def start(self):
        self.status = MoEnum.LiftLevellingStatus.Executing

        # Create data pack
        self.laser_distance.set_pack_id(self.laser_distance.create_data_pack(task_id=self.task_id))
        print(f"[lift_levelling_module.py] data pack created, pack_id = {self.laser_distance.pack_id}")

        # Pass pack_id to leveling detector
        self.lld.set_pack_id(self.laser_distance.pack_id)

        # Set moving direction
        self.laser_distance.set_move_dir(LAEnum.LinearActuatorStatus.Extend.value)
        print(f"[lift_levelling_module.py] direction set, move_dir = {self.laser_distance.move_dir}")

        # Start laser distance Thread
        self.laser_distance.start()

        # Set time limit of extend/ retract movement
        self.linear_actuator.set_time_limit(30.0)

        # Start linear actuator Thread
        self.linear_actuator.start()
        
        self.laser_distance.run_thread.join()
        self.linear_actuator.run_thread.join()
        
        


if __name__ == "__main__":
    def status_summary():
        status = '{"battery": 97.996, "position": {"x": 105.40159891291846, "y": 67.38314149752657, "theta": 75.20575899303867}, "map_id": 2, "map_rm_guid": "277c7d6f-2041-4000-9a9a-13f162c9fbfc"}'
        return status
    # Example usage:
    
    config = umethods.load_config('../../../conf/config.properties')
    port_config = umethods.load_config('../../../conf/port_config.properties')
    modb = NWDB.TopModuleDBHandler(config, status_summary)
    
    ll = LiftLevellingModule(modb, config, port_config, status_summary)
    # ll.pack_id = ll.create_data_pack(task_id=0)

    # threading.Thread(target=ll.thread_get_status).start()4

    # print(ll.nwdb.GetDistanceResult(side="left", pack_id=64, move_dir=2))

    ll.start()
    # time.sleep(35)
    
    # ll.start()

    # # Create data pack
    # ll.laser_distance.set_pack_id(ll.laser_distance.create_data_pack(task_id=1))
    # print(f"pack created, pack_id = {ll.laser_distance.pack_id}")

    # # Set moving direction
    # ll.laser_distance.set_move_dir(LAEnum.LinearActuatorStatus.Extend.value)
    # print(f"direction indicator set, move_dir = {ll.laser_distance.move_dir}")

    # # Start laser distance Thread
    # ll.laser_distance.start()

    # # Set time limit of extend/ retract movement
    # ll.linear_actuator.set_time_limit(20.0)

    # # Start linear actuator Thread
    # ll.linear_actuator.start()
