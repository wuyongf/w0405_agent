import src.top_module.db_top_module as MODB
import src.utils.methods as umethods
import src.top_module.analysis.layout_meshing as LayoutMeshing

class MeshDifference:
    
    def __init__(self, modb, meshing_1, meshing_2):
        self.modb = modb
        self.meshing_1 = meshing_1
        self.meshing_2 = meshing_2
        self.x_grid_min = 0
        self.x_grid_max = 0
        self.y_grid_min = 0
        self.y_grid_max = 0
        
    def findMaxMin(self, x, y):
        if x < self.x_grid_min or self.x_grid_min == 0:
            self.x_grid_min = x
        if x > self.x_grid_max or self.x_grid_max == 0:
            self.x_grid_max = x
        if y < self.y_grid_min or self.y_grid_min == 0:
            self.y_grid_min = y
        if y > self.y_grid_max or self.y_grid_max == 0:
            self.y_grid_max = y
            
            
    def intersection_of_lists(self, dict1, dict2):
        # Create a set of grid_ids from both dictionaries
        grid_ids1 = set(item['grid_id'] for item in dict1)
        grid_ids2 = set(item['grid_id'] for item in dict2)
        # Find the common grid_ids in both sets
        common_grid_ids = grid_ids1.intersection(grid_ids2)
        result_dict_1 = [item for item in dict1 if item['grid_id'] in common_grid_ids]
        result_dict_2 = [item for item in dict2 if item['grid_id'] in common_grid_ids]
        # print('d1', result_dict_1)
        # print('d2', result_dict_2)
        obj1 = {}
        obj2 = {}
        
        for i in result_dict_1:
            obj1[i['grid_id']] = i['value']
        for i in result_dict_2:
            obj2[i['grid_id']] = i['value']
            
        # print("*******", obj1)
        # print("*******", obj2)
        
        return common_grid_ids, obj1, obj2
        
        
    def get_difference_list(self):
        # Create intergrate list of two task
        integrate_list_1 = self.meshing_1.createIntergrateList(205)
        integrate_list_2 = self.meshing_2.createIntergrateList(207)
        intersection, grid_value_1, grid_value_2 = self.intersection_of_lists(integrate_list_1, integrate_list_2)
        # intersection = {'x109y23', 'x119y26', 'x114y26', 'x110y23', 'x111y21'}
       
        # Get difference and form a list
        obj_list = []
        for grid_str in intersection:
            obj={} # {'grid_id': 'x111y21', 'x_grid': 111, 'y_grid': 21, 'value': 144.0}
            obj['grid_id'] = grid_str
            obj['x_grid'] = int(grid_str.split('x')[1].split('y')[0])
            obj['y_grid'] = int(grid_str.split('x')[1].split('y')[1])
            value_1 = grid_value_1[str(grid_str)]
            value_2 = grid_value_2[str(grid_str)]
            value = abs(value_1 - value_2)
            obj['value'] = value
            # print(grid_str, value_1, value_2)
            obj_list.append(obj)
            
        for i in obj_list:
            x = i['x_grid']
            y = i['y_grid']
            self.findMaxMin(x, y)
            
        print("Result: ", obj_list)
        # print(self.x_grid_min, self.x_grid_max, self.y_grid_min, self.y_grid_max)

        self.meshing_2.plotHeatMap(obj_list, self.x_grid_min, self.x_grid_max, self.y_grid_min, self.y_grid_max)


if __name__ == "__main__":

    def status_summary():
        status = '{"battery": 97.996, "position": {"x": 1520, "y": 761, "theta": 75.20575899303867}, "map_id": 7, "map_rm_guid": "277c7d6f-2041-4000-9a9a-13f162c9fbfc"}'
        return status
    
    config = umethods.load_config('../../../conf/config.properties')
    port_config = umethods.load_config('../../../conf/port_config.properties')
    modb = MODB.TopModuleDBHandler(config, status_summary)
    meshing_1 = LayoutMeshing.LayoutMeshing(modb)
    meshing_2 = LayoutMeshing.LayoutMeshing(modb)
    
    md = MeshDifference(modb, meshing_1, meshing_2)
    meshing_1.set_task_id(205)
    meshing_2.set_task_id(206)
    # print(md.meshing_1.task_id)
    # print(md.meshing_2.task_id)
    md.get_difference_list()