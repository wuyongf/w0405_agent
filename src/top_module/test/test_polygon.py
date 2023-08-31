from shapely.geometry import Point
from shapely.geometry.polygon import Polygon
import json

data = '[{"x":411.1025804799999,"y":1550.0737827600003},{"x":763.3336523199999,"y":1556.3861675600003},{"x":759.54622144,"y":1998.2531035600005},{"x":406.0526726399999,"y":1990.6782418000003}]'

def parseRegionData(data):
    parsed_data = json.loads(data)
    result_array = [(entry['x'], entry['y']) for entry in parsed_data]
    return result_array

print(parseRegionData(data))

def checkRegion(x, y, region):
    print(Polygon(region).contains(Point(x,y)))
    

point = Point(0.5, 0.5)
polygon = Polygon([(0, 0), (0, 1), (1, 1), (1, 0)])
# print(polygon.contains(point))

checkRegion(530,1500,parseRegionData(data))