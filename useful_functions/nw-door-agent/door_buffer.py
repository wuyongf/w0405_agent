import math

door_center = (128, 128)
door_radius = 30
car_position = (x, y)


# Calculate the distance. Calculate once, sort out the door order once.
distance = math.sqrt((car_position[0] - door_center[0]) ** 2 + (car_position[1] - door_center[1]) ** 2)

if distance <= door_radius:
    print("Car is inside the door circle.")
    # Pause the robot
    # Open the door
    # Resume the robot
else:
    print("Car is outside the door circle.")

class NWDoorAgent:

    def __init__(self):
        self.is_closed = True
        self.door_arr = []
        self.door_status_arr = []
        self.region_radius = 30
        self.robot_cur_pos = None
        pass

    def set_door_status(self, door_id, status):
        self.is_closed = status

    def get_door_is_closed(self, door_id):
        return self.is_closed()