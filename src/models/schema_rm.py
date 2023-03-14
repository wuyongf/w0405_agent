# Created Date: 27 Jan 2023
# version ='1.0'
# ---------------------------------------------------------------------------
"""NCS RM API Definitions and Customize Object"""
# ---------------------------------------------------------------------------

# Python 3.9.15
# definition.py

# class RMStatus:
#     def __init__(self, batteryPct, state, mapPose):
#         self.batteryPct = batteryPct
#         self.state = state

class Status:
    def __init__(self, batteryPct, state, mapPose):
        self.batteryPct = batteryPct
        self.state = state
        self.mapPose = mapPose

class mapPose:
    def __init__(self, mapId = '', x = 0.0, y = 0.0, heading = 0.0):
        self.mapId = mapId
        self.x = x
        self.y = y
        self.heading = heading

class Task1:
    def __init__(self, taskId, task_type, parameters):
        self.taskId = taskId
        self.taskType = task_type
        self.parameters = parameters

class Task:
    def __init__(self, taskId, scheduleType, priority, task_type, parameters):
        self.taskId = taskId
        self.scheduleType = scheduleType
        self.priority = priority
        self.taskType = task_type
        self.parameters = parameters

class TaskStatus:
    def __init__(self, taskId, taskType, taskStatusType, errMsg = ''):
        self.taskId = taskId
        self.taskType = taskType
        self.taskStatusType = taskStatusType
        self.errMsg = errMsg

class JobUpdate:
    def __init__(self, id, name, tasks):
        self.id = id
        self.name = name
        self.tasks = tasks

# To create Job/Task
class TaskParams:
    def __init__(self, dct):
        self.mapId = dct['mapId']
        self.positionName = dct['positionName']
        self.x = dct['x']
        self.y = dct['y']
        self.heading = dct['heading']

# to receive mtqq task json
class Task:
    def __init__(self, dct):
        self.taskId = dct['taskId']
        self.scheduleType = dct['scheduleType']
        self.priority = dct['priority']
        self.taskType = dct['taskType']
        self.parameters = TaskParams(dct['parameters'])

# Built-In-Parameters: RM-GOTO/RM-LOCALIZE
class RMGOTO:
    def __init__(self, mapId, positionName, x, y, heading):
        self.mapId = mapId
        self.positionName = positionName
        self.x = x
        self.y = y
        self.heading = heading

class RMREMOTEESTOP:
    def __init__(self, estop=False):
        self.estop = estop

class RMLIGHT:
    def __init__(self, light=False):
        self.light = light