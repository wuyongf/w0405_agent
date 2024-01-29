# for MiR demo
import logging
import logging.handlers as handlers
import os
import time
import sys
import threading
import subprocess
import json
import src.utils.methods as umethods

import src_mir.handlers.status_handler_mir as status_handler
import src_mir.handlers.task_handler_mir as task_handler
import src_mir.models.robot_mir as MiRRobot

def run_robot_agent():

    # Change to the desired directory
    directory = "~/dev/robot-agent-v2.0/"
    os.chdir(os.path.expanduser(directory))

    # Run the shell script
    script_path = "./run-agent.sh"
    subprocess.run(["bash", script_path])

if __name__ == '__main__':

    # # Store the current directory
    # previous_directory = os.getc-wd()

    # # Create a thread and start it
    # thread = threading.Thread(target=run_robot_agent)
    # thread.start()

    # # Change back to the previous directory
    # os.chdir(previous_directory)

    # Sleep for 30 seconds for Pi to connect to MiR network...
    time.sleep(2)

    # Logging...

    # # Loading config files
    config = umethods.load_config('../conf/config_mir.properties')
    port_config = umethods.load_config('../conf/port_config.properties')
    skill_config_dir = '../conf/rm_skill.properties'
    ai_config = umethods.load_config('./ai_module/lift_noise/cfg/config.properties')

    # Robot
    mir_robot = MiRRobot.Robot(config, port_config, skill_config_dir, ai_config)
    mir_robot.status_start()

    # Status handler updates robot status every second
    status_handler = status_handler.StatusHandler(mir_robot)
    status_handler.start()

    # # Task handler subscribes and execute task, also report task status to robotmanager
    task_handler = task_handler.TaskHandler(mir_robot)
    task_handler.start()

    # # Remote Control Handler
    # remote_control_handler = remote_control_handler.RemoteControlHandler(mir_robot)
    # remote_control_handler.start()

    # # NW Door Agent
    # # nw_door_agent = NWDoorAgent(robot)
    # nw_door_agent = NWDoorRegionAgent(mir_robot)

    # # Robot Init
    # time.sleep(2)
    # localize_str = '{"id": 0, "name": "ChargingStation", "mapName": "EMSD_4F_2806_1", "x": -0.16755342017872188, "y": 54.501362814789175, "angle": 0.0}'
    # # robot.localize(json.loads(localize_str))

    # Successfully started the app
    print('main finished')