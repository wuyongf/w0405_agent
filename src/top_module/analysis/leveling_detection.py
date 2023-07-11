import time
import src.utils.methods as umethods
import src.top_module.db_top_module as NWDB

# TODO: Loop the function 4 times (L,R,extent,retract), Return the biggest result
#       Publish nomal level alert if one or more set of data fail
#       Publish emergency level alert if all set of data fail
#       Fail if the different between biggest and smallest result is > 2
#       Push the data to the rule analysis system

class lift_leveling_detection:
    def __init__(self, config):
        self.nwdb = NWDB.TopModuleDBHandler(config)
        self.data = []
        self.empty_region = []
        self.list_rate_of_change = []
        self.pack_id = 0
        self.result_stack = []

    def set_pack_id(self, pack_id):
        self.pack_id = pack_id

    def set_data(self, data):
        self.data = data
        
    def to_number_list(self, data):
        return list(map(int, data))

    # Calculate the rate of change and return a list:
    def calculate_rate_of_change(self, numbers):
        rates = []
        for i in range(1, len(numbers)):
            if numbers[i] != 0 and numbers[i-1] != 0:
                rate = (numbers[i] - numbers[i-1]) / numbers[i-1]
                rates.append(rate)
        return rates

    # Find the empty region between the floor and the lift
    # def find_empty_region(self, lst, maxi):
    #     start_index = None
    #     end_index = None
    #     for i in range(len(lst)):
    #         if lst[i] > 600:
    #             if start_index is None:
    #                 start_index = i
    #             end_index = i
    #     if end_index - start_index < maxi:
    #         return None
    #     return [start_index, end_index]
    def find_empty_region(self, lst, maxi):
        start_index = None
        end_index = None
        if len(lst) == 0:
            return None
        for i in range(len(lst)):
            if lst[i] > 600:
                if start_index is None:
                    start_index = i
                end_index = i
        if end_index is None:
            return None
        if end_index - start_index < maxi:
            return None
        return [start_index, end_index]

    # Find the region in list that have constant value in given range, retrun the middle index of the region
    def find_constant_region(self, lst, range_value):
        for i in range(len(lst) - range_value + 1):
            region = lst[i:i+range_value]
            if len(set(region)) == 1:
                # return [i, i + range_value - 1]
                # return int(round(((i + range_value - 1)+i)/2, 0))
                return i + int(round(range_value/2))
        print('fail')
        return -1

    # Extract region from a list
    def extract_region(self, lst, i_start, i_end):
        if i_start < 0 or i_end >= len(lst) or i_start > i_end:
            return None
        region = lst[i_start:i_end+1]
        return region

    # Run
    def level_detection(self):
        # Convert the data list to list of number
        self.data = self.to_number_list(self.data)
        
        try:
            self.empty_region = (self.find_empty_region(lst=self.data, maxi=20))
            print( self.empty_region)
            self.list_rate_of_change = self.calculate_rate_of_change(self.data)

            # Find the region before empty region
            before_i_start = self.empty_region[0]-50
            before_i_end = self.empty_region[0]
            region_before_empty = self.extract_region(
                lst=self.list_rate_of_change, i_start=before_i_start, i_end=before_i_end)

            # Find the region after empty region
            after_i_start = self.empty_region[1]
            after_i_end = self.empty_region[1]+50
            region_after_empty = self.extract_region(lst=self.list_rate_of_change, i_start=after_i_start, i_end=after_i_end)
            print(region_after_empty)
            # Locate the index of the region before and after empty region
            index_before_empty = self.find_constant_region(lst=region_before_empty, range_value=20) + before_i_start
            index_after_empty = self.find_constant_region(lst=region_after_empty, range_value=20) + after_i_start

            # Find the height before and after the empty
            height_before_empty = self.data[index_before_empty]
            height_after_empty = self.data[index_after_empty]

            print(index_before_empty)
            print(index_after_empty)

            result = abs(height_before_empty - height_after_empty)
            print(f"[levelling_detection.py] result: {result}" )
            return result
        # Return -1 if fail to get
        except:
            return -1
    
    def start_detection(self):
        side = ['left', 'right']
        direction = [2, 3]
        
        # Find result for each side, extent and retract
        for s in side:
            for d in direction:
                # print("[leveling_detection.py]" ,s, d)
                # TODO: pack_id = self.pack_id
                self.set_data(self.nwdb.GetDistanceResult(side=s, pack_id=self.pack_id, move_dir=d))
                time.sleep(0.1)
                result = self.level_detection()
                self.result_stack.append(result)
                
        # Update result to nwdb
        db_header = ["result_el", "result_rl", "result_er", "result_rr"]
        for i,r in enumerate(self.result_stack):
            self.nwdb.UpdateDistanceResult(column=db_header[i], id=self.pack_id, result=r)
        
                
                
                
        


if __name__ == "__main__":
    config = umethods.load_config('../../../conf/config.properties')    
    lfd = lift_leveling_detection(config)
    
    # NOTE: Print the result by given data:
    # print(lfd.level_detection())
    lfd.set_pack_id(87)
    
    lfd.start_detection()
