# NW Door Agent - Rev01 -  2023.07.06
import math, time, threading
import src.models.robot as Robot
import src.utils.methods as umethods
from src.models.schema.nw import Door

class NWDoorAgent:
    def __init__(self, robot: Robot.Robot):
        self.robot = robot
        self.doors = []

        # door buffer
        self.door_radius = 20 # 20 pixel == 100 cm

        # logic: nw-door-agent
        self.start_check_flag = True
        self.global_check_flag = False
        self.detail_check_flag = False

        # the closet door status and index
        # self.door_too_close = False
        self.door_index = 0

        # thread
        thread_global_check = threading.Thread(target=self.global_check).start()
        thread_detail_check = threading.Thread(target=self.detail_check).start()

        thread_assgin_mission = threading.Thread(target=self.assign_door_handler_mission).start()
    # Logic
    def assign_door_handler_mission(self):
        while(True):
            if(self.robot.door_agent_start): 
                self.robot.door_agent_start = False
                self.start()
            if(self.robot.door_agent_finish): 
                self.robot.door_agent_finish = False
                self.end()
            time.sleep(1)            

    def start(self):
        print(f'[door_handler.start]: configure doors start...')
        self.configure_doors()
        print(f'[door_handler.start]: configure doors finish...')
        self.global_check_flag = True
        pass

    def end(self):
        self.global_check_flag = False
        pass

    def global_check(self):
        while(self.start_check_flag):

            while(self.global_check_flag):
                # check if continue
                if(self.start_check_flag is False or  self.global_check_flag is False): break
                
                # check distance - Rev01
                for index, door in enumerate(self.doors):
                    distance = math.sqrt((self.robot.robot_status.mapPose.x - door.pos_x) ** 2 + (self.robot.robot_status.mapPose.y - door.pos_y) ** 2)
                    if distance < self.door_radius: # 20 pixel == 100 cm
                        # robot
                        self.robot.pause_robot_task()
                        # logic 
                        self.door_index = index
                        self.global_check_flag = False
                        self.detail_check_flag = True
                        break
            time.sleep(1)
    
    def detail_check(self):
        while(self.start_check_flag):

            if(self.detail_check_flag):
                door_index = self.door_index
                # try to open the door
                try:
                    print(f'[door_handler.detail_check] try to open the door...')
                    time.sleep(3)
                    # door_is_open = self.robot.open_door()
                    door_is_open = True
                except:
                    pass
                if(door_is_open):
                    print(f'[door_handler.detail_check] door is openned...')

                    # self.robot.phone_start_rotating()
                    self.robot.resume_robot_task()

                    self.check_door_distance(door_index, break_loop_distance=30)
                    # self.robot.phone_stop_rotating()

                    # logic
                    self.detail_check_flag = False
                    self.global_check_flag = True
                break
            time.sleep(1)

    # Door

    def configure_doors(self):

        # get RV activated map --> get NWDB corresponding layout_id
        layout_id = self.robot.get_current_layout_id()

        # get door_ids from NWDB
        door_ids =  self.robot.nwdb.get_values('data.robot.map.layout.door.location', 'ID', 'layout_id', layout_id)
        
        # Assume door_ids is a list of door IDs retrieved from the database
        self.doors.clear()

        for door_id in door_ids:
            # Fetch the remaining properties from the database based on the door ID
            layout_id = self.robot.nwdb.get_single_value('data.robot.map.layout.door.location', 'layout_id', 'ID', door_id)
            name = self.robot.nwdb.get_single_value('data.robot.map.layout.door.location', 'name', 'ID', door_id)
            pos_x = self.robot.nwdb.get_single_value('data.robot.map.layout.door.location', 'pos_x', 'ID', door_id)
            pos_y = self.robot.nwdb.get_single_value('data.robot.map.layout.door.location', 'pos_y', 'ID', door_id)
            pos_heading = self.robot.nwdb.get_single_value('data.robot.map.layout.door.location', 'pos_heading', 'ID', door_id)

            # Create a Door object and append it to the list
            door = Door(layout_id, name, pos_x, pos_y, pos_heading, is_closed=True)
            self.doors.append(door)
        return self.doors

    def check_door_distance(self, index, break_loop_distance):
        
        while(True):

            distance = math.sqrt((self.robot.robot_status.mapPose.x - self.doors[index].pos_x) ** 2 + (self.robot.robot_status.mapPose.y - self.doors[index].pos_y) ** 2)

            if(distance >= break_loop_distance): break
            
            time.sleep(0.2)

    
if __name__ == '__main__':
    config = umethods.load_config('../../conf/config.properties')
    port_config = umethods.load_config('../../conf/port_config.properties')
    robot = Robot.Robot(config,port_config)

    door_handler = NWDoorAgent(robot)
    # status_handler.start()

    result = door_handler.list_doors()
    print(result)
    # door_handler.end()