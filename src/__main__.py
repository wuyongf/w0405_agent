import logging
import logging.handlers as handlers
import os
import time
import sys
import threading
import subprocess
# yf
import src.utils.methods as umethods
import handlers.status_handler as status_handler
import handlers.remote_control_handler as remote_control_handler
import handlers.task_handler3 as task_handler
import src.models.robot as Robot
import src.models.enums.nw as NWEnum

def run_robot_agent():


    # Change to the desired directory
    directory = "~/dev/robot-agent-v2.0/"
    os.chdir(os.path.expanduser(directory))

    # Run the shell script
    script_path = "./run-agent.sh"
    subprocess.run(["bash", script_path])



if __name__ == '__main__':

    # # Store the current directory
    # previous_directory = os.getcwd()

    # # Create a thread and start it
    # thread = threading.Thread(target=run_robot_agent)
    # thread.start()

    # # Change back to the previous directory
    # os.chdir(previous_directory)

    # Sleep for 30 seconds for Pi to connect to MiR network...
    time.sleep(2)

    # # Setup logging configs
    # if not os.path.exists('../../logs'):
    #     os.makedirs('../../logs')
    # logname = "../../logs/nw-rm-rv-app.log"
    # formatter = logging.Formatter('[%(asctime)s] [%(levelname)s] %(filename)s:%(lineno)d %(funcName)s(): %(message)s',
    #                               datefmt='%d-%b-%y %H:%M:%S')
    # logHandler = handlers.TimedRotatingFileHandler(logname, when='D', interval=1, backupCount=30, encoding='utf-8')
    # logHandler.setFormatter(formatter)
    # logStreamHandler = logging.StreamHandler(sys.stdout)
    # logStreamHandler.setFormatter(formatter)

    # logger = logging.getLogger('')
    # logger.addHandler(logStreamHandler)
    # logger.addHandler(logHandler)
    # logger.setLevel(logging.INFO)

    # # Loading config files
    config = umethods.load_config('../conf/config.properties')
    port_config = umethods.load_config('../conf/port_config.properties')

    # 
    robot = Robot.Robot(config, port_config)
    robot.status_start(NWEnum.Protocol.RVMQTT)
    robot.sensor_start()

    # Status handler updates robot status every second
    status_handler = status_handler.StatusHandler(robot)
    status_handler.start()

    # # Task handler subscribes and execute task, also report task status to robotmanager
    task_handler = task_handler.TaskHandler(robot)
    task_handler.start()

    # Remote Control Handler
    remote_control_handler = remote_control_handler.RemoteControlHandler(config)
    remote_control_handler.start()

    # Successfully started the app
    # logging.getLogger('').info("rm-mir-app successfully started!")
    print('main finished')

