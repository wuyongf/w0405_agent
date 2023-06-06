
# TODO: Loop the function 4 times (L,R,extent,retract), Return the biggest result
#       Publish nomal level alert if one or more set of data fail
#       Publish emergency level alert if all set of data fail
#       Fail if the different between biggest and smallest result is > 2
#       Push the data to the rule analysis system

class lift_leveling_detection:
    def __init__(self):
        # self.data = [488, 488, 488, 488, 488, 488, 488, 488, 488, 488, 488, 488, 488, 488, 488, 488, 488, 488, 488, 488, 488, 488, 488, 488, 488, 488, 488, 488, 488, 488, 488, 488, 488, 488, 488, 488, 488, 488, 488, 488, 488, 488, 488, 488, 488, 488, 488, 488, 488, 488, 488, 488, 488, 488, 488, 488, 488, 488, 488, 488, 488, 488, 488, 488, 488, 488, 488, 488, 488, 488, 488, 488, 488, 488, 488, 488, 488, 488, 488, 488, 488, 488, 488, 488, 488, 488, 488, 488, 488, 488, 488, 488, 488, 488, 488, 488, 488, 488, 488, 488, 488, 488, 488, 488, 488, 488, 488, 488, 488, 488, 488, 488, 488, 488, 488, 488, 488, 488, 488, 487, 487, 487, 487, 487, 487, 487, 487, 487, 487, 487, 487, 487, 487, 487, 487, 487, 487, 487, 487, 487, 487, 487, 492, 492, 492, 500, 500, 509, 518, 518, 518, 518, 519, 519, 519, 519, 519, 519, 519, 519, 519, 519, 519, 519, 519, 519, 519, 519, 519, 519, 519, 513, 505, 505, 495, 491, 489, 489, 489, 489, 489, 489, 489, 489, 489, 489, 489, 489, 489, 489, 489, 488, 488, 488, 488, 488, 488, 488, 488, 488, 488, 488, 488, 488, 488, 488, 488, 488, 488, 488, 488, 488, 488, 488, 488, 488, 488, 488, 488, 488, 488, 488, 488, 488, 488, 488, 488, 488, 488, 488, 488, 488, 488, 488, 488, 488, 488, 488, 488, 488, 488, 488, 488, 488, 488, 488, 488, 488, 488, 488, 488, 488, 488, 488, 488, 488, 488, 488, 488, 488, 488, 488, 488, 488, 488, 488, 488, 488, 488, 488, 488, 488, 488, 488, 488, 488, 488, 486, 469, 469, 469, 469, 469, 469, 469, 469, 700, 700, 700, 700, 700, 700, 700, 700, 700, 700, 700, 700, 700, 700, 700, 700, 700, 700, 700, 700, 700, 700, 700, 700, 700, 700, 700, 700, 700, 700, 700, 700, 700, 700, 700, 700, 700, 700, 700, 700, 700, 700, 700, 700, 700, 700, 700, 700, 700, 700, 700, 700, 700, 700, 700, 700, 700, 700, 700, 700, 700, 700, 700, 700, 700, 490, 490, 490, 490, 490, 490, 490, 490, 490, 490, 490, 487, 487, 487, 487, 487, 487, 487, 487, 487, 487, 487, 487, 487, 487, 487, 487, 487, 487, 487, 487, 487, 487, 487, 487, 487, 487, 487,
        #  487, 487, 487, 487, 487, 487, 487, 487, 487, 487, 487, 487, 487, 487, 487, 487, 487, 487, 487, 487, 487, 487, 487, 487, 487, 487, 487, 487, 487, 487, 487, 487, 488, 488, 488, 488, 488, 488, 488, 488, 488, 488, 488, 488, 488, 488, 488, 488, 488, 488, 488, 488, 488, 488, 488, 488, 488, 488, 488, 488, 488, 488, 488, 488, 488, 488, 488, 488, 488, 488, 488, 492, 499, 510, 510, 510, 510, 512, 514, 514, 516, 518, 518, 518, 518, 518, 518, 518, 518, 518, 518, 518, 518, 518, 518, 518, 518, 518, 518, 515, 507, 507, 507, 498, 491, 489, 487, 487, 487, 487, 487, 487, 487, 487, 487, 487, 487, 487, 487, 487, 487, 487, 487, 487, 487, 487, 487, 487, 487, 487, 487, 487, 487, 487, 487, 487, 487, 487, 487, 487, 487, 487, 487, 487, 487, 487, 487, 487, 487, 487, 487, 487, 487, 487, 487, 487, 487, 487, 487, 487, 487, 487, 487, 487, 487, 487, 487, 487, 487, 487, 487, 487, 487, 487, 487, 487, 487, 487, 487, 487, 487, 487, 487, 487, 487, 487, 487, 487, 487, 487, 487, 487, 487, 487, 487, 487, 487, 487, 487, 487, 487, 487, 487, 487, 487, 487, 487, 487, 487, 487, 487, 487, 487, 487, 487, 487, 487, 487, 487, 487, 487, 487, 487, 487, 487, 487, 487, 487, 487, 487, 487, 487, 487, 487, 487, 487, 487, 487, 487, 487, 487, 487, 487, 487, 487, 487, 487, 487, 487, 487, 487, 487, 487, 487, 487, 487, 487, 487, 487, 487, 487, 487, 487, 487, 487, 487, 487, 487, 487, 487, 487, 487, 487, 487, 487, 487, 487, 487, 487, 487, 487, 487, 487, 487, 487, 487, 487, 487, 487, 487, 487, 487, 487, 487, 487, 487, 487, 487, 487, 487, 487, 487, 487, 487, 487, 487, 487, 487, 487, 487, 487, 487, 487, 487, 487, 487, 487, 487, 487, 487, 487, 487, 487, 487, 487, 487, 487, 487, 487, 487, 487, 487, 487, 487, 487, 487, 487, 487, 487, 487, 487, 487, 487, 487, 487, 487, 487, 487, 487, 487, 487, 487, 487, 487, 487, 487, 487, 487, 487, 487, 487, 487, 487, 487, 487, 487, 487, 487, 487, 487, 487, 487, 487, 487, 487, 487, 487, 487, 487, 487, 487, 487, 487, 487, 487, 487, 487, 487, 487, 487, 487, 487]
        self.data = []
        self.empty_region = []
        self.list_rate_of_change = []

    def set_data(self, data):
        self.data = data

    # Calculate the rate of change and return a list:
    def calculate_rate_of_change(self, numbers):
        rates = []
        for i in range(1, len(numbers)):
            if numbers[i] != 0 and numbers[i-1] != 0:
                rate = (numbers[i] - numbers[i-1]) / numbers[i-1]
                rates.append(rate)
        return rates

    # Find the empty region between the floor and the lift
    def find_empty_region(self, lst, maxi):
        start_index = None
        end_index = None
        for i in range(len(lst)):
            if lst[i] > 600:
                if start_index is None:
                    start_index = i
                end_index = i
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
        return False

    # Extract region from a list
    def extract_region(self, lst, i_start, i_end):
        if i_start < 0 or i_end >= len(lst) or i_start > i_end:
            return None
        region = lst[i_start:i_end+1]
        return region

    # Run
    def level_detection(self):
        self.empty_region = (self.find_empty_region(lst=self.data, maxi=50))
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

        # Locate the index of the region before and after empty region
        index_before_empty = self.find_constant_region(lst=region_before_empty, range_value=30) + before_i_start
        index_after_empty = self.find_constant_region(lst=region_after_empty, range_value=30) + after_i_start

        # Find the height before and after the empty
        height_before_empty = self.data[index_before_empty]
        height_after_empty = self.data[index_after_empty]

        print(height_before_empty)
        print(height_after_empty)

        result = abs(height_before_empty - height_after_empty)
        return result


if __name__ == "__main__":
    lfd = lift_leveling_detection()
    print(lfd.level_detection())
