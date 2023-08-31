import json
import src.top_module.db_top_module as NWDB
import src.utils.methods as umethods
import time
import src.top_module.analysis.event_publisher as event_publisher


class UserRulesChecker():
    def __init__(self, modb, header_list, status_summary):
        # self.modb = NWDB.TopModuleDBHandler(config)
        self.modb = modb
        self.header_list = header_list
        # self.status_summary = status_summary
        self.event_publisher = event_publisher.EventPublisher('localhost', status_summary)
    
    def get_rules_column(self, dataset, column):
        return [i.get(column) for i in dataset]
    
    def check_stack(self, data_stack):
        # mySQL get (type, threshold, limit_type) as list
        rules_list = self.modb.GetUserRules()
        # print(rules_list)
        rules_type_list = self.get_rules_column(rules_list, "data_type")
        rules_threshold_list = self.get_rules_column(rules_list, "threshold")
        rules_limit_type_list = self.get_rules_column(rules_list, "limit_type")
        rules_name_list = self.get_rules_column(rules_list, "name")
        rules_activated_list = self.get_rules_column(rules_list, "activated")
        rules_severity_list = self.get_rules_column(rules_list, "severity")
        data_type_alreadypublish = []

        for data in data_stack:
            pos_x = data[len(data)-2]
            pos_y = data[len(data)-1]
            print(f"[user_rules.py] x: {pos_x} , y: {pos_y}" )
            
            for row_num, data_type in enumerate(rules_type_list):
                try:
                    # Compare with rules_type_list, find the index of data
                    col_idx = self.header_list.index(data_type)
                    threshold = rules_threshold_list[row_num]
                    limit_type = rules_limit_type_list[row_num]
                    name = rules_name_list[row_num]
                    activated = rules_activated_list[row_num]
                    severity = rules_severity_list[row_num]
                    value = data[col_idx]

                    print(
                        f"[user_rules.py] Checking: {value}, Rule Name: {name}, Data Type: {data_type}, Column Index: {col_idx}, Limit Type: {limit_type}, Threshold: {threshold}")

                    if (limit_type == "HIGH" and value > threshold) or (limit_type == "LOW" and value < threshold) and activated == 1:
                        print(
                            f"[user_rules.py] ***Rule Name: {name}, Type: {data_type}, Threshold: {threshold}, Value: {value}")
                        
                        if data_type not in data_type_alreadypublish:
                            time.sleep(1)
                            self.publish_event(value=value, name= name, data_type= data_type, threshold=threshold, severity=severity)
                            time.sleep(1)
                            data_type_alreadypublish.append(data_type)
                            print(data_type_alreadypublish)
                            

                except ValueError:
                    # print(
                    #     f"No matched data type for rule data type {data_type}")
                    pass
                    
    def publish_event(self, value, name, data_type, threshold, severity):
        title = f"Sensor Value Alert: {name}"
        description = f"Rule Name: {name}, Data Type: {data_type}, Threshold: {threshold}, Value: {value}"
        
        self.event_publisher.add_title(title)
        self.event_publisher.add_severity(severity)
        self.event_publisher.add_description(description)
        self.event_publisher.add_mapPose()
        self.event_publisher.add_empty_medias()
        self.event_publisher.publish()
        # self.event_publisher.publish_test()
        
                    

if __name__ == "__main__":
    config = umethods.load_config('../../conf/config.properties')
    port_config = umethods.load_config('../../conf/port_config.properties')
