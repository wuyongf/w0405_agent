# Created Date: 27 Jan 2023
# version ='1.0'
# ---------------------------------------------------------------------------
"""NCS RM API Definitions and Customize Object"""
# ---------------------------------------------------------------------------

# Python 3.9.15
# definition.py
import json
import uuid


class Status:
    def __init__(self, batteryPct, state, mapPose, layoutPose):
        self.batteryPct = batteryPct
        self.state = state
        self.mapPose = mapPose
        self.layoutPose = layoutPose

    def to_json(self):
        return json.dumps(self.__dict__, default=lambda o: o.__dict__)


class mapPose:
    def __init__(self, mapId='', x=0.0, y=0.0, heading=0.0):
        self.mapId = mapId
        self.x = x
        self.y = y
        self.heading = heading

    def to_json(self):
        return json.dumps(self.__dict__)

class layoutPose:
    def __init__(self, layoutId='', x=0.0, y=0.0, heading=0.0):
        self.layoutId = layoutId
        self.x = x
        self.y = y
        self.heading = heading

    def to_json(self):
        return json.dumps(self.__dict__)
    
class doorPose:
    pass

# class Task1:
#     def __init__(self, taskId, task_type, parameters):
#         self.taskId = taskId
#         self.taskType = task_type
#         self.parameters = parameters

# class Task:
#     def __init__(self, taskId, scheduleType, priority, task_type, parameters):
#         self.taskId = taskId
#         self.scheduleType = scheduleType
#         self.priority = priority
#         self.taskType = task_type
#         self.parameters = parameters


class TaskStatus:
    def __init__(self, taskId, taskType, taskStatusType, errMsg=''):
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
    def __init__(self, dct=None):
        if dct is None: return None
        else:
            self.mapId = dct['mapId']
            self.positionName = dct['positionName']
            self.x = dct['x']
            self.y = dct['y']
            self.heading = dct['heading']
            if(type(self.heading == str)):
                self.heading = int(self.heading)


# to receive mtqq task json
class Task:
    def __init__(self, dct=None):
        if dct is None:
            print('task_json is NULL')
            return None
        else:
            self.taskId = dct['taskId']
            self.scheduleType = dct['scheduleType']
            self.priority = dct['priority']
            self.taskType = dct['taskType']


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


class RMFOLLOWME:
    def __init__(self, mode=False, pairingState=False):
        self.mode = mode
        self.state = pairingState


# Event
class Meida:
    def __init__(self, filePath, type, title, view360=False):
        self.filePath = filePath
        self.type = type  # 1: image 2: video
        self.title = title
        self.__dict__['360View'] = view360


class EventWithoutMedia:
    def __init__(self, title, severity, description, mapPose=mapPose):
        self.eventId = str(uuid.uuid1())
        self.title = title
        self.severity = severity  # 1: critical 2: normal
        self.description = description
        # self.medias = medias
        self.mapPose = mapPose
        # self.metadata = metadata

    def to_json(self):
        return json.dumps(self.__dict__, default=lambda o: o.__dict__)

class Event:
    def __init__(self, title, severity, description, mapPose=mapPose, medias=[], metadata={}):
        self.eventId = str(uuid.uuid1())
        self.title = title
        self.severity = severity  # 1: critical 2: normal
        self.description = description
        self.medias = medias
        self.mapPose = mapPose
        self.metadata = metadata

    def to_json(self):
        return json.dumps(self.__dict__, default=lambda o: o.__dict__)
    
# Layout_map
class LayoutMapList:
    def __init__(self, imageWidth, imageHeight, scale, angle, translate):
        self.imageWidth = imageWidth
        self.imageHeight = imageHeight
        self.scale = scale
        self.angle = angle
        self.translate = translate

    def to_json(self):
        return json.dumps(self.__dict__, default=lambda o: o.__dict__)

# Door
class Door:
    def __init__(self, id, name, startPoint, endPoint, motionAxis, motionDegree, motionDirection, graphVertexId):
        self.id = id
        self.name = name
        self.startPoint = startPoint
        self.endPoint = endPoint
        self.motionAxis = motionAxis
        self.motionDegree = motionDegree
        self.motionDirection = motionDirection
        self.graphVertexId = graphVertexId

    def parse(self, dct):
        self.id = dct["id"]
        self.name = dct["name"]
        self.startPoint = dct["startPoint"]
        self.endPoint = dct["endPoint"]
        self.motionAxis = dct["motionAxis"]
        self.motionDegree = dct["motionDegree"]
        self.motionDirection = dct["motionDirection"]
        self.graphVertexId = dct["graphVertexId"]

    def to_json(self):
        return json.dumps(self.__dict__, default=lambda o: o.__dict__)

if __name__ == '__main__':
    # media_info_list = []
    # media_info_list.append(Meidas("C:/dev/w0405_agent/useful_functions/ncs_demo_codes/event-images/front_right.png", 1, "Front Right", False))
    # media_info_list.append(Meidas("C:/dev/w0405_agent/useful_functions/ncs_demo_codes/event-images/front_right.png", 1, "Front Right", False))
    # media_json = json.dumps(media_info_list, default=lambda o: o.__dict__)
    # print(media_json)

    # to publish an event
    # 1. event title.   (str)
    # 2. severity.      (int) (1: critical 2: normal)
    # 3. description    (str)
    # 4. mapPose_json   (str)
    # 5. medias_json    (str) (optional)
    # 6. metadata       (str) (optional)

    # 1, 2 and 3
    title = 'event_test_rev01'
    severity = 1
    description = 'This is an event test'

    # 4.
    map_pose = mapPose()
    mapPose_json = map_pose.to_json()
    # mapPose_json = robot.get_current_mapPose().to_json()

    # 5.
    medias = []
    medias.append(
        Meida("D:/Dev/w0405_agent/src/data/event-images/20230331_145659_0001/front_right.png", 1, "Front Right"))

    print('XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX')

    event1_json = Event(title, severity, description, map_pose, medias).to_json()
    print(event1_json)
