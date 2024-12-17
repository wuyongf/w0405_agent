import logging
import logging.handlers as handlers
import os
import time
import sys
import threading
import subprocess
import json
# yf
import src.utils.methods as umethods
import handlers.status_handler as status_handler
import handlers.remote_control_handler as remote_control_handler
import handlers.task_handler as task_handler
from src.handlers.door_handler_nwdb import NWDoorAgent, NWDoorRegionAgent
import src.models.enums.nw as NWEnum
import src.models.robot as Robot
# import src.models.mir_robot as Robot

if __name__ == '__main__':

    # time.sleep(90)

    # # Loading config files
    config = umethods.load_config('../conf/config.properties')
    port_config = umethods.load_config('../conf/port_config.properties')
    skill_config_dir = '../conf/rm_skill.properties'
    ai_config = umethods.load_config('./ai_module/lift_noise/cfg/config.properties')

    # Robot
    robot = Robot.Robot(config, port_config, skill_config_dir, ai_config)
    robot.init()
    robot.status_start(NWEnum.Protocol.RVMQTT)
    robot.sensor_start()

    # Status handler updates robot status every second
    status_handler = status_handler.StatusHandler(robot)
    status_handler.start()

    # # Task handler subscribes and execute task, also report task status to robotmanager
    task_handler = task_handler.TaskHandler(robot)
    task_handler.start()

    # Remote Control Handler
    remote_control_handler = remote_control_handler.RemoteControlHandler(robot)
    remote_control_handler.start()

    # NW Door Agent
    # nw_door_agent = NWDoorAgent(robot)
    nw_door_agent = NWDoorRegionAgent(robot)

    # Robot Init
    time.sleep(5)
    # Successfully started the app
    print('main finished')
    time.sleep(5)

    # print('init localization')
    # from src.publishers.pub_mission import MissionPublisher
    # pub = MissionPublisher(skill_config_dir, robot.rmapi)
    # pub.const_Charging_off(6)
    # time.sleep(10)
    # pub.const_bootup_localization(current_floor_id=6)