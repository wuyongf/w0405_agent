import src.top_module.db_top_module as MODB
import src.utils.methods as umethods
import numpy as np
import matplotlib.pyplot as plt

class LayoutMeshing:

    def __init__(self, modb):
        self.modb = modb
        self.mesh_size = 12
        self.task_id = 0
        self.data_list_raw = []
        self.data_list = []
        self.integrate_list = []
        self.data_type = "lux"
        self.x_grid_min = 0
        self.x_grid_max = 0
        self.y_grid_min = 0
        self.y_grid_max = 0

    def set_mesh_size(self, mesh_size):
        self.mesh_size = mesh_size

    def set_task_id(self, task_id):
        self.task_id = task_id

    def set_data_type(self, data_type):
        self.data_type = data_type

    def getIaqDataList(self):
        self.data_list_raw = self.modb.GetIaqData(self.task_id)

    def split(self, point, meshsize):
        return (int(point / meshsize) + (point % meshsize > 0))

    def findMaxMin(self, x, y):
        if x < self.x_grid_min or self.x_grid_min == 0:
            self.x_grid_min = x
        elif x > self.x_grid_max:
            self.x_grid_max = x
        if y < self.y_grid_min or self.y_grid_min == 0:
            self.y_grid_min = y
        elif y > self.y_grid_max:
            self.y_grid_max = y

    def formatList(self):
        newlist = []
        obj = {}

        for i in self.data_list_raw:
            obj = {}
            x = i["pos_x"]
            y = i["pos_y"]
            x_grid = self.split(x, self.mesh_size)
            y_grid = self.split(y, self.mesh_size)
            self.findMaxMin(x_grid, y_grid)

            # obj["x"] = x
            # obj["y"] = y
            obj["grid_id"] = f"x{str(x_grid)}y{str(y_grid)}"
            obj["x_grid"] = x_grid
            obj["y_grid"] = y_grid
            obj['value'] = i[self.data_type]
            # obj['data_type'] = self.data_type
            # obj['task_id'] = self.task_id
            newlist.append(obj)

        self.data_list = newlist
        print(self.data_list)

    def integrateList(self):
        integrate_list = []
        for i in self.data_list:
            # girdId = i['grid_id']
            # if intergrate_list contains same grid_id
            if (next((item for item in integrate_list if item["grid_id"] == i['grid_id']), None)):
                current_value = (next(item for item in integrate_list if item["grid_id"] == i['grid_id']))['value']
                extend_value = i['value']
                new_value = (current_value + extend_value) / 2
                print(i['grid_id'], current_value, extend_value, new_value)
                # print("included", i['grid_id'])

            else:
                obj = {}
                obj['grid_id'] = i['grid_id']
                obj["x_grid"] = i['x_grid']
                obj["y_grid"] = i['y_grid']
                obj['value'] = i['value']
                integrate_list.append(obj)
                # print('not included, append', i['grid_id'])

        print(integrate_list)
        print("number of grids: ", len(integrate_list))
        
        self.integrate_list = integrate_list
        return (integrate_list)


    def createHeatMap(self):
        canvas_size_x = self.x_grid_max - self.x_grid_min
        canvas_size_y = self.y_grid_max - self.y_grid_min
        heat_map = np.zeros((canvas_size_y + 1, canvas_size_x + 1))
        for i in self.integrate_list:
            x = i['x_grid'] - self.x_grid_min
            y = i['y_grid'] - self.y_grid_min
            print(x,y)
            heat_map[y][x] = i['value']
        print(heat_map)
        fig, ax = plt.subplots()
        im = ax.imshow(heat_map)
        plt.show()

    def createLuxHeatMap(self, task_id):
        self.set_task_id(task_id)
        self.set_data_type("lux")
        self.getIaqDataList()
        self.formatList()
        self.integrateList()
        self.createHeatMap()

    def compareLuxHeatMap(self, task_id_1, task_id_2):
        self.set_data_type("lux")
        self.set_task_id(task_id_1)
        self.getIaqDataList()
        self.formatList()
        list_1 = self.integrateList()
        self.createHeatMap()

if __name__ == "__main__":

    def status_summary():
        status = '{"battery": 97.996, "position": {"x": 1520, "y": 761, "theta": 75.20575899303867}, "map_id": 7, "map_rm_guid": "277c7d6f-2041-4000-9a9a-13f162c9fbfc"}'
        return status

    config = umethods.load_config('../../../conf/config.properties')
    port_config = umethods.load_config('../../../conf/port_config.properties')
    modb = MODB.TopModuleDBHandler(config, status_summary)

    lm = LayoutMeshing(modb)
    lm.createLuxHeatMap(205)
    
    # lm.set_task_id(206)
    # lm.set_data_type("lux")
    # lm.getIaqDataList()
    # # print(lm.data_list_raw)
    # lm.formatList()
    # lm.integrateList()
    # lm.createHeatMap()

    # print(lm.x_grid_min, lm.x_grid_max, lm.y_grid_min, lm.y_grid_max)
    # print("canvas size: ", lm.x_grid_max - lm.x_grid_min, ", ", lm.y_grid_max - lm.y_grid_min)

    # print(lm.data_list)
