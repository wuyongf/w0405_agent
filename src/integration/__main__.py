import src.integration.handlers.status_handler as status_handler
# import rm.integration.mir200.handlers.task_handler as task_handler
import logging
import logging.handlers as handlers
import os
import time
import sys
from jproperties import Properties

if __name__ == '__main__':
    # Sleep for 30 seconds for Pi to connect to MiR network...
    time.sleep(2)

    # Setup logging configs
    if not os.path.exists('../../logs'):
        os.makedirs('../../logs')
    logname = "../../logs/nw-rm-rv-app.log"
    formatter = logging.Formatter('[%(asctime)s] [%(levelname)s] %(filename)s:%(lineno)d %(funcName)s(): %(message)s',
                                  datefmt='%d-%b-%y %H:%M:%S')
    logHandler = handlers.TimedRotatingFileHandler(logname, when='D', interval=1, backupCount=30, encoding='utf-8')
    logHandler.setFormatter(formatter)
    logStreamHandler = logging.StreamHandler(sys.stdout)
    logStreamHandler.setFormatter(formatter)

    logger = logging.getLogger('')
    logger.addHandler(logStreamHandler)
    logger.addHandler(logHandler)
    logger.setLevel(logging.INFO)

    # # Loading config files
    rv_config_addr = '../../conf/rv/rv-config.properties'

    # Status handler updates robot status every second
    sh = status_handler.StatusHandler(rv_config_addr, "localhost", "/robot/status")
    sh.publish_status()
    # # Task handler subscribes and execute task, also report task status to robotmanager
    # th = task_handler.TaskHandler("localhost", 1883, "/robot/task", "/robot/task/status")

    # Successfully started the app
    logging.getLogger('').info("rm-mir-app successfully started!")

