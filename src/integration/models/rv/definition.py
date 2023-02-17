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
    def __init__(self, upDown, leftRight, turboOn = False):
        self.upDown = upDown
        self.leftRight = leftRight
        self.turboOn = turboOn