#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#----------------------------------------------------------------------------
# Created By  : Yongfeng, NW
# Created Date: 27 Jan 2023
# version ='1.0'
# ---------------------------------------------------------------------------
"""RV API Definitions and Customize Object"""
# ---------------------------------------------------------------------------

# Python 3.9.15
# definition.py


class BatteryState:
    def __init__(self, dct):
        self.robotId = dct['robotId']
        self.percentage = dct['percentage']
        self.powerSupplyStatus = dct['powerSupplyStatus']


class Pose:
    def __init__(self, dct):
        self.robotId = dct['robotId']
        self.mapName = dct['mapName']
        self.x = dct['x']
        self.y = dct['y']
        self.angle = dct['angle']


class Waypoint:
    def __init__(self):
        self.id = 0
        self.name = ''
        self.mapName = ''
        self.x = 0.0
        self.y = 0.0
        self.angle = 0.0


class ActiveMap:
    def __init__(self, dct):
        self.robotId = dct['robotId']
        self.id = dct['id']
        self.name = dct['name']


class MapMetadata:
    def __init__(self, dct=None):
        # if dct is None: return None
        # print(dct)
        self.resolution = dct['resolution']
        self.width = dct['width']
        self.height = dct['height']
        self.x = dct['x']
        self.y = dct['y']
        self.angle = dct['angle']


class Mode:
    def __init__(self, dct):
        self.robotId = dct['robotId']
        self.state = dct['state']
        self.followMeStandalone = dct['followMeStandalone']
        self.manual = dct['manual']


class FollowMe:
    def __init__(self, dct):
        self.robotId = dct['robotId']
        self.pairingState = dct['pairingState']


class MQTTJoyStick:
    def __init__(self, object):
        self.id = "joystick"
        # self.topicName = "rvautotech/fobo/joystick"
        # self.className = "com.rvautotech.fobo.amr.dto.JoystickDTO"
        self.message = object


class MQTTTopic:
    def __init__(self, id, topicName, className, object):
        self.id = id
        self.topicName = topicName
        self.className = className
        self.object = object


class MQTTObjJoyStick:
    def __init__(self, upDown, leftRight, turboOn=False):
        self.upDown = upDown
        self.leftRight = leftRight
        self.turboOn = turboOn