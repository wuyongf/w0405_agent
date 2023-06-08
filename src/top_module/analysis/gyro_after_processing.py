import numpy as np
from scipy.signal import savgol_filter
import src.utils.methods as umethods
import src.top_module.db_top_module as NWDB


# TODO: function to pull from db, filtering, split into chunk and update

class gyro_after_processing:
    def __init__(self, config) -> None:
        self.nwdb = NWDB.TopModuleDBHandler(config)
        self.pack_id
    
    def set_pack_id(self, pack_id):
        self.pack_id = pack_id
    
    def noise_filtering(self, data):
        return savgol_filter(data, 51, 3)

    def calculate_rate_of_change(self, data):
        rates = []
        for i in range(1, len(data)):
            rate = (data[i] - data[i-1]) / data[i-1]
            rates.append(rate)
        return rates

if __name__ == "__main__":
    config = umethods.load_config('../../../conf/config.properties')
    gap = gyro_after_processing(config)


