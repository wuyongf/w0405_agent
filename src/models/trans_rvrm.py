import math
import src.models.schema_rv as RVSchema

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
        waypoint.y = (self.map_height - pixel_y) * self.map_resolution + self.rv_origin_y
       
        if 0 <= heading <= 270.0:
            waypoint.angle = - (heading - 90.0) * math.pi / 180.0
        if 270 < heading <= 360.0:
            waypoint.angle = (- (heading - 360.0) + 90 ) * math.pi / 180.0
        print(f'rv_heading: {waypoint.angle * 180.0 / math.pi}')
        # print(f'rv pose(x,y,theta) is ({rv_x},{rv_y},{rv_angle})')
        return waypoint
    
    # def waypoint_rm2rv2(self, pixel_x, pixel_y, heading):
    #     rv_x =  (pixel_x * self.map_resolution + self.rv_origin_x )
    #     rv_y =  ((self.map_height - pixel_y) * self.map_resolution + self.rv_origin_y)
    #     if heading <= 180.0:
    #         rv_angle = heading * math.pi / 180.0
    #     else: rv_angle = -(360.0 - heading) * math.pi/180.0
    #     print(f'rv pose(x,y,theta) is ({rv_x},{rv_y},{rv_angle})')

    def waypoint_rv2rm(self, rv_x, rv_y, rv_angle):
        pixel_x = (rv_x - self.rv_origin_x)/self.map_resolution
        pixel_y = self.map_height - (rv_y - self.rv_origin_y)/self.map_resolution
        if math.pi >= rv_angle >= -2*math.pi:
            heading =  - rv_angle * 180.0 / math.pi + 90.0
        if 2*math.pi >= rv_angle > math.pi:
            heading = - rv_angle * 180.0 / math.pi + 270.0
        # print(f'rm pixel(x,y,theta) is ({pixel_x},{pixel_y},{heading})')
        return  pixel_x, pixel_y, heading

    def pos_rm2bim(self):
        pass

if __name__ == '__main__':
    
    trans  = RVRMTransform()
    # define rv origin
    trans.rv_origin_x = -3.249993
    trans.rv_origin_y = -2.75
    # define rv map width and height
    trans.map_height = 150
    trans.map_width = 96
    # get pos rm2rv

    # pixel_x = 64.625
    # pixel_y = 95.125 # (0.018742999999999732,2.70625)
    # heading = 359
    # trans.waypoint_rm2rv2(pixel_x, pixel_y, heading)

    # rv_x = 0.018742999999999732
    # rv_y = 2.70625 
    # rv_heading = -.0001 # (64.625,95.125)
    # trans.waypoint_rv2rm(rv_x, rv_y, rv_heading)



    # rm 73.651, 85.3057
    # rv "x": -0.4325826933855703, "y": -0.48471240135094806


    # rv_x = 0.4325570000000001
    # rv_y = 0.484715
    # rv_heading = -.0001 
    # trans.waypoint_rv2rm(rv_x, rv_y, rv_heading)

    # pixel_x = 71.152 
    # pixel_y = 89.096
    # heading = 359
    # # trans.waypoint_rm2rv2(pixel_x, pixel_y, heading)

    heading = 360
    # res = - (heading - 90.0) * math.pi / 180.0
    res = (- (heading - 360.0) + 90 ) * math.pi / 180.0
    print(res)

    # 1.57 -> -3.14

    # 3.14 -> 1.57