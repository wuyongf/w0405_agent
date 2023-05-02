import src.top_module.db_top_module as NWDB
import src.utils.methods as umethods


class user_rules():
    def __init__(self, config):
        self.nwdb = NWDB.robotDBHandler(config)

    def check_stack(self, data_stack):
        # mySQL get (type, threshold, limit_type) as list
        rules_list = self.nwdb.GetUserRules()
        print(rules_list)
        rules_type_list = self.get_rules_column(rules_list, "data_type")
        rules_threshold_list = self.get_rules_column(rules_list, "threshold")
        rules_limit_type_list = self.get_rules_column(rules_list, "limit_type")
        rules_name_list = self.get_rules_column(rules_list, "name")

        for data in data_stack:
            for row_num, data_type in enumerate(rules_type_list):
                try:
                    # Compare with rules_type_list, find the index of data
                    col_idx = self.column_items.index(data_type)
                    threshold = rules_threshold_list[row_num]
                    limit_type = rules_limit_type_list[row_num]
                    name = rules_name_list[row_num]
                    value = data[col_idx]

                    print(
                        f"Checking: {value}, Rule Name: {name}, Data Type: {data_type}, Column Index: {col_idx}, Limit Type: {limit_type}, Threshold: {threshold}")

                    if limit_type == "HIGH" and value > threshold:
                        print(
                            f"*** Higher than threshold, Rule Name: {name}, Type: {data_type}, Threshold: {threshold}, Value: {value}")
                            # publish event
                            # insert log

                    elif limit_type == "LOW" and value < threshold:
                        print(
                            f"*** Lower than threshold, Rule Name: {name}, Type: {data_type}, Threshold: {threshold}, Value: {value}")
                            

                except ValueError:
                    print(
                        f"No matched data type for rule data type {data_type}")


if __name__ == "__main__":
    config = umethods.load_config('../../conf/config.properties')
