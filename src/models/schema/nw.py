import json
import uuid

class Status:
    def __init__(self, battery, position, map_id, map_rm_guid):
        self.battery = battery
        self.position = position
        self.map_id = map_id
        self.map_rm_guid = map_rm_guid
    def to_json(self):
        return json.dumps(self.__dict__, default=lambda o: o.__dict__)
    
class Position:
    def __init__(self, x, y, theta):
        self.x = x
        self.y = y
        self.theta = theta
    def to_json(self):
        return json.dumps(self.__dict__, default=lambda o: o.__dict__)
    
# Charging
class ChargingStation:
    def __init__(self, layout_nw_id, layout_rm_guid, map_id, map_rm_guid, pos_name, pos_x, pos_y, pos_theta):
        self.layout_nw_id = layout_nw_id
        self.layout_rm_guid = layout_rm_guid
        self.map_id = map_id
        self.map_rm_guid = map_rm_guid
        self.pos_name = pos_name
        self.pos_x = pos_x
        self.pos_y = pos_y
        self.pos_theta = pos_theta
    def to_json(self):
        return json.dumps(self.__dict__, default=lambda o: o.__dict__)
# Lift
class LiftMission:
    def __init__(self, lift_id, robot_id, 
                 cur_layout_id, cur_floor_int, cur_waiting_pos_id, cur_transit_pos_id,
                 target_layout_id, target_floor_int, target_waiting_pos_id, target_transit_pos_id, target_out_pos_id,
                 liftmap_layout_id, liftmap_in_pos_id, liftmap_transit_pos_id, liftmap_out_pos_id):
        self.lift_id = lift_id
        self.robot_id = robot_id
        self.cur_layout_id = cur_layout_id
        self.cur_floor_int = cur_floor_int
        self.cur_waiting_pos_id = cur_waiting_pos_id
        self.cur_transit_pos_id = cur_transit_pos_id

        self.target_layout_id = target_layout_id
        self.target_floor_int = target_floor_int
        self.target_waiting_pos_id = target_waiting_pos_id
        self.target_transit_pos_id = target_transit_pos_id
        self.target_out_pos_id = target_out_pos_id

        self.liftmap_layout_id = liftmap_layout_id
        self.liftmap_in_pos_id = liftmap_in_pos_id
        self.liftmap_transit_pos_id = liftmap_transit_pos_id
        self.liftmap_out_pos_id =liftmap_out_pos_id


    def to_json(self):
        return json.dumps(self.__dict__, default=lambda o: o.__dict__)
    
class LiftPose:
    def __init__(self, layout_guid = '', map_guid = '', pos_name = '', x = 0.0, y = 0.0, heading = 0.0):
        self.layout_guid = layout_guid
        self.map_guid = map_guid
        self.pos_name = pos_name
        self.x = x
        self.y = y
        self.heading = heading
    def to_json(self):
        return json.dumps(self.__dict__)

# Delivery
class DeliveryMission:
    def __init__(self, ID, robot_id, sender_id, pos_origin_id, receiver_id, pos_destination_id):
        self.ID = ID
        self.robot_id = robot_id
        self.sender_id = sender_id
        self.pos_origin_id = pos_origin_id
        self.receiver_id = receiver_id
        self.pos_destination_id = pos_destination_id
    def to_json(self):
        return json.dumps(self.__dict__, default=lambda o: o.__dict__)
    
class DeliveryPose:
    def __init__(self, layout_guid = '', map_guid = '', pos_name = '', x = 0.0, y = 0.0, heading = 0.0):
        self.layout_guid = layout_guid
        self.map_guid = map_guid
        self.pos_name = pos_name
        self.x = x
        self.y = y
        self.heading = heading
    def to_json(self):
        return json.dumps(self.__dict__)

class DeliveryPerson:
    def __init__(self, name_en = '', name_cn = '', number = '', email = ''):
        self.name_en = name_en
        self.name_cn = name_cn
        self.number = number
        self.email = email
    def to_json(self):
        return json.dumps(self.__dict__)
    

# Door

class Door:
    def __init__(self, layout_id, name, pos_x, pos_y, pos_heading, is_closed = True):
        self.layout_id = layout_id
        self.name = name
        self.pos_x = pos_x
        self.pos_y = pos_y
        self.pos_heading = pos_heading
        self.is_closed = is_closed
    def to_json(self):
        return json.dumps(self.__dict__, default=lambda o: o.__dict__)
    
class DoorRegion:
    def __init__(self, name, polygon, layout_id, is_closed = True):
        self.name = name
        self.polygon = polygon
        self.layout_id = layout_id
        self.is_closed = is_closed
    def to_json(self):
        return json.dumps(self.__dict__, default=lambda o: o.__dict__)