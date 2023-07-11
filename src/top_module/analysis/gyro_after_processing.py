import numpy as np
from scipy.signal import savgol_filter
import src.utils.methods as umethods
import src.top_module.db_top_module as NWDB


# TODO: function to pull from db, filtering, split into chunk and update

class gyro_after_processing:
    def __init__(self, config) -> None:
        self.nwdb = NWDB.TopModuleDBHandler(config)
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
        raw_data = self.nwdb.GetGyroResult(pack_id)
        print(raw_data)
        denoise_data = self.noise_filtering(raw_data)
        list_to_str = ','.join([str(elem) for elem in denoise_data])
        self.nwdb.UpdateGyroResult(id=pack_id, column='result_denoise', result=list_to_str)

if __name__ == "__main__":
    config = umethods.load_config('../../../conf/config.properties')
    gap = gyro_after_processing(config)
    
    # result = gap.nwdb.GetGyroResult(21)
    # data = gap.noise_filtering(result)
    # list_to_str = ','.join([str(elem) for elem in data])
    # print(list_to_str)
    # # print((gap.noise_filtering(result)))
    # gap.nwdb.UpdateGyroResult(id=21, column='result_denoise', result=list_to_str)
    
    gap.after_processing(18)

