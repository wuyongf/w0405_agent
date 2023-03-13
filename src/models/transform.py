import math

class Transform:
    def __init__(self):
        self.map_resolution = 0.05
        self.map_width = self.map_height = 0
        self.rv_origin_x = self.rv_origin_y = self.rv_origin_angle = 0.0
        # self.rm_origin_x = self.rm_origin_y = self.rm_origin_angle = 0.0

    def origin_rv2rm(self, width, height, x, y, angle):
        origin_rm_x = abs(x)/self.map_resolution
        origin_rm_y = self.map_height - abs(y)/self.map_resolution
        pass

    def pos_rm2rv(self, pixel_x, pixel_y, heading):
        rv_x = - (pixel_x * self.map_resolution + self.rv_origin_x )
        rv_y = - ((self.map_height - pixel_y) * self.map_resolution + self.rv_origin_y)
        if heading <= 180.0:
            rv_angle = heading * math.pi / 180.0
        else: rv_angle = -(360.0 - heading) * math.pi/180.0
        # print(f'rv pose(x,y,theta) is ({rv_x},{rv_y},{rv_angle})')

    def pos_rv2rm(self, rv_x, rv_y, rv_angle):
        pixel_x = -(rv_x + self.rv_origin_x)/self.map_resolution
        pixel_y = (self.map_height*self.map_resolution + (rv_y + self.rv_origin_y))/self.map_resolution
        if rv_angle >= 0.0:
            heading = rv_angle * 180.0 / math.pi
        else: heading = (180.0 - abs(rv_angle) * 180.0 / math.pi) + 180.0
        # print(f'rm pixel(x,y,theta) is ({pixel_x},{pixel_y},{heading})')    

if __name__ == '__main__':
    
    trans  = Transform()
    # define rv origin
    trans.rv_origin_x = -3.249993
    trans.rv_origin_y = -2.75
    # define rv map width and height
    trans.map_height = 96
    trans.map_width = 150
    # get pos rm2rv

    pixel_x = 64.625
    pixel_y = 95.125 # (0.018742999999999732,2.70625)
    heading = 359
    trans.pos_rm2rv(pixel_x, pixel_y, heading)

    rv_x = 0.018742999999999732
    rv_y = 2.70625 
    rv_heading = -.0001 # (64.625,95.125)
    trans.pos_rv2rm(rv_x, rv_y, rv_heading)
