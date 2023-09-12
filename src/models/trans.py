# for RVRMTransform
import math
import src.models.schema.rv as RVSchema
# for RMLayoutMapTransform
from math import pi, cos, sin
import numpy as np
from numpy.linalg import inv

class RVRMTransform:
    def __init__(self):
        self.map_resolution = 0.05
        self.map_width = 0
        self.map_height = 0
        self.rv_origin_x = self.rv_origin_y = self.rv_origin_angle = 0.0

    def update_rv_map_info(self, map_width, map_height, rv_origin_x, rv_origin_y, rv_origin_angle):
        self.map_resolution = 0.05
        self.map_width = map_width
        self.map_height = map_height
        self.rv_origin_x = rv_origin_x
        self.rv_origin_y = rv_origin_y
        self.rv_origin_angle = rv_origin_angle

    def clear_rv_map_info(self):
        self.map_resolution = 0.05
        self.map_width = 0.0
        self.map_height = 0.0
        self.rv_origin_x = 0.0
        self.rv_origin_y = 0.0
        self.rv_origin_angle = 0.0

    def origin_rv2rm(self, width, height, x, y, angle):
        origin_rm_x = abs(x)/self.map_resolution
        origin_rm_y = self.map_height - abs(y)/self.map_resolution
        pass

    def waypoint_rm2rv(self, map_name, point_name, pixel_x, pixel_y, heading):
        # print(f'self.map_resolution = {self.map_resolution }')
        # print(f'self.map_width      = {self.map_width      }')
        # print(f'self.map_height     = {self.map_height     }')
        # print(f'self.rv_origin_x    = {self.rv_origin_x    }')
        # print(f'self.rv_origin_y    = {self.rv_origin_y    }')
        # print(f'self.rv_origin_angle= {self.rv_origin_angle}')
        # print(f'self.rm_x={pixel_x}')
        # print(f'self.rm_y={pixel_y}')
        # print(f'self.rm_heading={heading}')
        waypoint = RVSchema.Waypoint()
        waypoint.mapName = map_name
        waypoint.name = point_name
        waypoint.x = pixel_x * self.map_resolution + self.rv_origin_x
        waypoint.y = (self.map_height - pixel_y) * \
            self.map_resolution + self.rv_origin_y

        if 0 <= heading <= 270.0:
            waypoint.angle = - (heading - 90.0) * math.pi / 180.0
        if 270 < heading <= 360.0:
            waypoint.angle = (- (heading - 360.0) + 90) * math.pi / 180.0
        print(f'rv_heading: {waypoint.angle * 180.0 / math.pi}')
        # print(f'rv pose(x,y,theta) is ({rv_x},{rv_y},{rv_angle})')
        return waypoint

    def waypoint_rv2rm(self, rv_x, rv_y, rv_angle):
        pixel_x = (rv_x - self.rv_origin_x)/self.map_resolution
        pixel_y = self.map_height - \
            (rv_y - self.rv_origin_y)/self.map_resolution
        if -math.pi <= rv_angle < math.pi/2:
            heading = - rv_angle * 180.0 / math.pi + 90.0
        if math.pi/2 <= rv_angle <= math.pi:
            heading = - rv_angle * 180.0 / math.pi + (360.0 + 90.0)
        # print(f'rm pixel(x,y,theta) is ({pixel_x},{pixel_y},{heading})')
        return pixel_x, pixel_y, heading

    def pos_rm2bim(self):
        pass

class RMLayoutMapTransform:
    '''
    Translation between layout and map. Refernce: https://www.notion.so/W0405-DevLog-10fdc4d8771348719ccf8893b8e27aaa
    input: current position in reference to map
    output current position in reference to layout
    '''
    def __init__(self):
        pass

    def update_layoutmap_params(self, imageWidth, imageHeight, scale, angle, translate):
        self.map_width = imageWidth
        self.map_height = imageHeight
        self.map_scale = scale
        self.map_rotate_angle = angle
        self.map_center_translate = translate
        self.rotation_matrix = self.__cal_rotation_matrix()        
        pass

    def __cal_rotation_matrix(self):
        angle_rad = self.map_rotate_angle * (pi / 180)
        return np.array([
            [cos(angle_rad), -sin(angle_rad)],
            [sin(angle_rad), cos(angle_rad)]])

    def __find_map_origin_in_layout(self):
        translate_layout_center = np.array([[self.map_center_translate[0]], [self.map_center_translate[1]]])
        map_center = np.array([[self.map_width/2], [self.map_height/2]])
        t = np.matmul(self.rotation_matrix,map_center) * self.map_scale
        translation_map_origin = translate_layout_center - t

        return translation_map_origin

    def find_cur_layout_point(self, cur_map_x, cur_map_y, cur_map_theta):

        translation_map_origin = self.__find_map_origin_in_layout()

        cur_map_point = np.array([[cur_map_x], [cur_map_y]])
        rotated_point = np.matmul(self.rotation_matrix,cur_map_point)
        scaled_point = rotated_point * self.map_scale
        
        cur_layout_point = scaled_point + [translation_map_origin[0], translation_map_origin[1]]

        return cur_layout_point[0][0], cur_layout_point[1][0], cur_map_theta + self.map_rotate_angle
    
    def find_cur_map_point(self,cur_layout_x, cur_layout_y, cur_layout_theta):

        cur_layout_point = np.array([[cur_layout_x], [cur_layout_y]])
        translation_map_origin = self.__find_map_origin_in_layout()

        scaled_point = cur_layout_point - [translation_map_origin[0], translation_map_origin[1]]
        rotated_point = scaled_point / self.map_scale
        cur_map_point = np.matmul(inv(self.rotation_matrix),rotated_point)
        
        return cur_map_point[0][0], cur_map_point[1][0], cur_layout_theta - self.map_rotate_angle

def main_RVRMTransform():

    trans = RVRMTransform()
    # define rv origin
    trans.rv_origin_x = -3.249993
    trans.rv_origin_y = -2.75
    # define rv map width and height
    trans.map_height = 15
    trans.map_width = 96
    # get pos rm2rv

    # rv_x = 0.4325570000000001
    # rv_y = 0.484715
    # rv_heading = -.0001
    # trans.waypoint_rv2rm(rv_x, rv_y, rv_heading)

    # pixel_x = 71.152
    # pixel_y = 89.096
    # heading = 359
    # # trans.waypoint_rm2rv2(pixel_x, pixel_y, heading)

    rv_angle = math.pi/2
    # res = - (heading - 90.0) * math.pi / 180.0
    res = - rv_angle * 180.0 / math.pi + (360.0 + 90.0)
    print(res)

    # 1.57 -> -3.14

    # 3.14 -> 1.57

def main_RMLayoutMapTransform():
    T_RM = RMLayoutMapTransform()
    T_RM.update_layoutmap_params(2828, 1335, 0.39171, 6.70102, [1211.835, 359.122])

    cur_layout_point = T_RM.find_cur_layout_point(744, 592, 0)

    print(cur_layout_point)

    cur_map_point = T_RM.find_cur_map_point(954.63313433,299.12555485, 0)
    print(cur_map_point)

if __name__ == '__main__':

    # main_RVRMTransform()
    main_RMLayoutMapTransform()

