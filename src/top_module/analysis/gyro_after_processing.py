import numpy as np
from scipy.signal import savgol_filter
import src.utils.methods as umethods
import src.top_module.db_top_module as NWDB
import src.top_module.analysis.user_rules as rule


# TODO: function to pull from db, filtering, split into chunk and update

class gyro_after_processing:
    def __init__(self, modb, status_summary):
        # self.nwdb = NWDB.TopModuleDBHandler(config)
        self.modb = modb
        
        self.header_list_insert = ['lift_vibration']
        self.user_rules = rule.UserRulesChecker(self.modb, self.header_list_insert, status_summary)
        self.pack_id = 0
    
    def set_pack_id(self, pack_id):
        self.pack_id = pack_id
    
    def noise_filtering(self, data):
        np.set_printoptions(threshold=np.inf)  # Set print options to display full array
        filtered_data = savgol_filter(data, 51, 3)
        return filtered_data

    def calculate_rate_of_change(self, data):
        rates = []
        for i in range(1, len(data)):
            rate = (data[i] - data[i-1]) / data[i-1]
            rates.append(rate)
        return rates
    
    def after_processing(self, pack_id):
        # Query the raw data
        raw_data = self.modb.GetGyroResult(pack_id)
        
        #  Denoise the raw data
        denoise_data = self.noise_filtering(raw_data)
        
        #  Find the minimun & maximun in the denoised data
        minmax_list = find_min_max(denoise_data)
        result_min = minmax_list[0]
        result_max = minmax_list[1]
        
        # Wrappe the item in [] for rules checking
        wrapped_list = [[item] for item in minmax_list]
        # Check the data by user rules
        self.user_rules.check_stack(wrapped_list)
        
        list_to_str = ','.join([str(elem) for elem in denoise_data])
        self.modb.UpdateGyroResult(id=pack_id, column='result_denoise', result=list_to_str, result_min=result_min, result_max=result_max)

def find_min_max(input_list):
    min_val = max_val = input_list[0]
    for num in input_list:
        if num < min_val:
            min_val = num
        elif num > max_val:
            max_val = num

    return [min_val, max_val]

if __name__ == "__main__":
    def status_summary():
        status = '{"battery": 10.989, "position": {"x": 0.0, "y": 0.0, "theta": 0.0}, "map_id": null, "map_rm_guid: `277c7d6f-2041-4000-9a9a-13f162c9fbfc`"}'
        return status
    
    config = umethods.load_config('../../../conf/config.properties')
    port_config = umethods.load_config('../../../conf/port_config.properties')
    modb = NWDB.TopModuleDBHandler(config, status_summary)
    gap = gyro_after_processing(modb, status_summary)
    
    # result = gap.modb.GetGyroResult(21)
    # data = gap.noise_filtering(result)
    # list_to_str = ','.join([str(elem) for elem in data])
    # print(list_to_str)
    # # print((gap.noise_filtering(result)))
    # gap.modb.UpdateGyroResult(id=21, column='result_denoise', result=list_to_str)
    
    gap.after_processing(32)

