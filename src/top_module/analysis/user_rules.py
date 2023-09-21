import json
import src.top_module.db_top_module as NWDB
import src.utils.methods as umethods
import time
import src.top_module.analysis.event_publisher as event_publisher
import src.top_module.analysis.region_handler as region_handler


class UserRulesChecker():
    def __init__(self, modb, header_list, status_summary):
        # self.modb = NWDB.TopModuleDBHandler(config)
        self.modb = modb
        self.region_handler = region_handler.RegionHandler()
        self.header_list = header_list
        self.status_summary = status_summary
        self.event_publisher = event_publisher.EventPublisher('localhost', status_summary)
        self.map_id = -1
        self.layout_id = -1
        self.task_id = -1

    def get_map_id(self):
        obj = json.loads(self.status_summary())
        self.map_id = obj["map_id"]
        self.layout_id = self.modb.GetLayoutIdByMapId(self.map_id)

    def set_task_id(self, id):
        self.task_id = id

    def get_rules_column(self, dataset, column):
        return [i.get(column) for i in dataset]

    def check_stack(self, data_stack, task_id):
        self.get_map_id()
        self.set_task_id(task_id)
        # mySQL get (type, threshold, limit_type) as list
        rules_list = self.modb.GetUserRules()
        all_region_list = self.modb.GetRegionsByMapId(self.map_id)
        # print(rules_list)
        # print(f"map_id: {self.map_id}")
        # print(f"layout_id: {self.layout_id}")
        # print(f"region: {custom_region}")
        rules_ID_list = self.get_rules_column(rules_list, "ID")
        rules_type_list = self.get_rules_column(rules_list, "data_type")
        rules_threshold_list = self.get_rules_column(rules_list, "threshold")
        rules_limit_type_list = self.get_rules_column(rules_list, "limit_type")
        rules_name_list = self.get_rules_column(rules_list, "name")
        rules_activated_list = self.get_rules_column(rules_list, "activated")
        rules_severity_list = self.get_rules_column(rules_list, "severity")
        rules_region_list = self.get_rules_column(rules_list, "region_list")
        rules_layout_list = self.get_rules_column(rules_list, "layout_id")
        data_type_alreadypublish = []
        rule_id_alreadypublish = []

        for data in data_stack:
            pos_x = data[len(data)-2]
            pos_y = data[len(data)-1]
            # print(f"[user_rules.py] x: {pos_x} , y: {pos_y}" )
            
            for row_num, data_type in enumerate(rules_type_list):
                try:
                    # Compare with rules_type_list, find the index of data
                    col_idx = self.header_list.index(data_type)
                    rule_id = rules_ID_list[row_num]
                    threshold = rules_threshold_list[row_num]
                    limit_type = rules_limit_type_list[row_num]
                    name = rules_name_list[row_num]
                    activated = rules_activated_list[row_num]
                    severity = rules_severity_list[row_num]
                    value = data[col_idx]
                    region_str = rules_region_list[row_num]
                    layout_id = rules_layout_list[row_num]
                    # print(region_str)
                    polygon_id_list = []
                    polygon_list = [] 
                    is_inside_region = False
                    
                    if region_str != "" and region_str is not None:
                        polygon_id_list = [int(num) for num in region_str.split(',')]
                    
                    print(
                        f"[user_rules.py] Checking: {value}, Rule Name: {name}, Data Type: {data_type}, Column Index: {col_idx}, Limit Type: {limit_type}, Threshold: {threshold}, LayoutId: {layout_id}, RegionList: {polygon_id_list}")

                    # Check if data's layout id == rules layout id
                    # Global Ruls when layout_id == None
                    if layout_id == self.layout_id or layout_id is None:
                        print("[user_rules.py] Rules layout_id == currnet layout_id OR is global rules, Apply rules.")


                        if (limit_type == "HIGH" and value > threshold) or (limit_type == "LOW" and value < threshold) and activated == 1:
                            print(
                                f"[user_rules.py] ***Rule Name: {name}, Type: {data_type}, Threshold: {threshold}, Value: {value}")

                            # Get Polygon from rules by matching region Id
                            for pid in polygon_id_list:
                                for region in all_region_list:
                                    rid = region.get("ID")
                                    if pid == rid:
                                        polygon = self.region_handler.parseRegionData(region.get('polygon'))
                                        polygon_list.append(polygon)

                            print(f'[user_rules.py]  polygon_list: {polygon_list}')
                            
                            # Check Polygon
                            for polygon in polygon_list:
                                if self.region_handler.checkRegion(x=pos_x, y=pos_y, region=polygon) is True:
                                    is_inside_region = True
                                    
                            # is_inside_region = self.check_region(pos_x, pos_y, polygon_list)
                            if is_inside_region == True or polygon_list == []:
                                if rule_id not in rule_id_alreadypublish:
                                    # print("********************************************************")
                                    time.sleep(1)
                                    # self.modb.InsertEventLog(self.task_id, data_type, name, severity, threshold, pos_x, pos_y, self.layout_id)
                                    self.publish_event(value=value, name= name, data_type= data_type, threshold=threshold, severity=severity, x=pos_x, y=pos_y)
                                    time.sleep(1)
                                    rule_id_alreadypublish.append(rule_id)
                                # if data_type not in data_type_alreadypublish:
                                #     time.sleep(1)
                                #     self.publish_event(value=value, name= name, data_type= data_type, threshold=threshold, severity=severity, x=pos_x, y=pos_y)
                                #     time.sleep(1)
                                #     data_type_alreadypublish.append(data_type)
                            

                except ValueError:
                    print(
                        f"[user_rules.py] No matched data type for rule data type {data_type}")
                    pass
                    
    def publish_event(self, value, name, data_type, threshold, severity, x, y):
        title = f"Sensor Value Alert: {name}"
        description = f"Rule Name: {name}, Data Type: {data_type}, Threshold: {threshold}, Value: {value}"
        
        self.event_publisher.add_title(title)
        self.event_publisher.add_severity(severity)
        self.event_publisher.add_description(description)
        self.event_publisher.add_mapPose(x,y)
        self.event_publisher.add_empty_medias()
        event_id = self.event_publisher.publish()
        self.modb.InsertEventLog(self.task_id, data_type, name, severity, threshold, x, y, self.layout_id, event_id)
    # def InsertEventLog(self, task_id, data_type, rule_name, severity, rule_threshold, pos_x, pos_y, layout_id):
        # self.event_publisher.publish_test()
        
    def check_region(self,x ,y ,polygon_list):
        for polygon in polygon_list:
            if self.region_handler.checkRegion(x=x, y=y, region=polygon) is True:
                print("[user_rules.py] ***************************Inside Polygon*****************************")
                return True

if __name__ == "__main__":
    config = umethods.load_config('../../conf/config.properties')
    port_config = umethods.load_config('../../conf/port_config.properties')
