import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import savgol_filter
import ast

class GyroAnalyzer:
    '''
    analyser and visualizer
    '''
    def __init__(self,):
        self.descrete_gyro_data = None
        self.time_array = None
        self.gyro_data  = None
        self.smmothed_gyro_data = None

        # analysis: large changes
        self.travelling_indices = None
        pass

    def load_gyro_compact_info(self, file_dir):
        with open(file_dir, 'r') as f:
            lines = f.readlines()
        self.descrete_gyro_data = [[list(map(float, ast.literal_eval(item)[0].split(','))), float(ast.literal_eval(item)[1])] for item in lines]
        return self.descrete_gyro_data

    def algin_gyro_with_timestampe(self, descrete_gyro_data):
        # Prepare the dataset
        timestamps = np.array([item[1] for item in descrete_gyro_data])
        self.gyro_data = np.concatenate([item[0] for item in descrete_gyro_data])
        
        # Assuming that gyro data is collected at regular intervals, compute time array
        self.time_array = np.linspace(0, timestamps[-1], len(self.gyro_data))
        return self.time_array, self.gyro_data
    
    def smmoth_gyro_data(self, raw_gyro_data, window_length=81, polyorder=7):
        '''Smooth the data using Savitzky-Golay filter'''
        # smoothed_gyro_data = savgol_filter(gyro_data, window_length=51, polyorder=3)
        self.smoothed_gyro_data = savgol_filter(raw_gyro_data, window_length, polyorder)
        return self.smoothed_gyro_data       
    
    ## Find Large Changes for the Gyro data
    def find_large_changes(self, factor=1.1):
        gyro_derivative = np.gradient(self.smoothed_gyro_data)
        threshold = np.std(gyro_derivative)/factor  # Example threshold based on standard deviation
        self.travelling_indices = np.where(abs(gyro_derivative) > threshold)[0]
        # print(time_array[self.travelling_indices])

        # Group the timestamps into ranges
        self.grouped_ranges = self.group_timestamps(time_array[self.travelling_indices])
        # Format the grouped ranges
        self.formatted_ranges = self.format_grouped_ranges(self.grouped_ranges)
        # print(formatted_ranges)    
        pass

    def group_timestamps(self, timestamps, max_gap=5):
        grouped_ranges = []
        range_start = timestamps[0]

        for i in range(1, len(timestamps)):
            if timestamps[i] - timestamps[i - 1] > max_gap:
                # Finish the current range and start a new one
                grouped_ranges.append([range_start, timestamps[i - 1]])
                range_start = timestamps[i]

        # Add the final range
        grouped_ranges.append([range_start, timestamps[-1]])
        return grouped_ranges

    def format_grouped_ranges(self, grouped_ranges):
        formatted_list = []
        for start, end in grouped_ranges:
            # Calculate the length of the range, assuming integer seconds
            length = int(end) - int(start) + 1
            formatted_list.append([length, start, end])
        return formatted_list
    
    ## Visualizer
    def plot(self, figsize, xlabel, ylabel, title,
             time_array, gyro_data, label, alpha):
        """Plots gyro data."""
        plt.figure(figsize)
        plt.plot(time_array, gyro_data, label = label, alpha = alpha)
        plt.xlabel(xlabel)
        plt.ylabel(ylabel)
        plt.title(title)
        plt.legend()
        plt.show()
    
    def plot_smoothed_gyro_data(self):
        """Plots gyro data."""
        plt.figure(figsize=(10, 6))
        plt.plot(self.time_array, self.gyro_data, label='Original', alpha=0.5)
        plt.plot(self.time_array, self.smoothed_gyro_data, label='Smoothed', linewidth=2)
        plt.xlabel('Time (frames)')
        plt.ylabel('Gyro Data')
        plt.title('Gyro Data Smoothing')
        plt.legend()
        plt.show()

    def plot_large_changes(self):
        plt.figure(figsize=(10, 6))
        plt.plot(self.time_array, self.gyro_data, label='Original', alpha=0.5)
        plt.plot(self.time_array, self.smoothed_gyro_data, label='Smoothed', linewidth=2)
        plt.scatter(self.time_array[self.travelling_indices], self.smoothed_gyro_data[self.travelling_indices], color='red', label='Lift Travelling')
        plt.xlabel('Time (sec)')
        plt.ylabel('Gyro Data')
        plt.title('Lift Travelling Range Detection')
        plt.legend()
        plt.show()

    ## Analyzer
    def slice_gyro_data(self, start_sec, end_sec, gyro_data):
        # Find the indices corresponding to the start and end times
        start_index = np.argmax(self.time_array >= start_sec)
        end_index = np.argmax(self.time_array >= end_sec)

        return self.time_array[start_index:end_index], gyro_data[start_index:end_index]

    def get_acc_direction(self, gyro_duration_data):
        '''
        y = ax^3 + bx^2 + cx + d
        '''
        gyro_derivative = np.gradient(gyro_duration_data)
        gyro_second_derivative = np.gradient(gyro_derivative)

        # # [method-1] cal acc: Compute the first derivative of the smoothed data
        acc = np.mean(gyro_second_derivative)
        if(acc >=0): return 'up'
        else: return 'down'

        # # [method-2] cal delta
        # delta = gyro_second_derivative[-1] - gyro_second_derivative[0]
        # if(delta >=0): return 'up'
        # else: return 'down'
        

if __name__ == '__main__':

    ga = GyroAnalyzer()

    # gyro_compact_info_dir = 'gyro_compact_info.txt'
    gyro_compact_info_dir = 'gyro_compact_info_531.txt'
    descrete_gyro_data = ga.load_gyro_compact_info(gyro_compact_info_dir)
    time_array, gyro_data = ga.algin_gyro_with_timestampe(descrete_gyro_data)
    smoothed_gyro_data = ga.smmoth_gyro_data(gyro_data, window_length=81, polyorder=7)
    
    sliced_gyro_data = ga.slice_gyro_data(start_sec=9.382, end_sec=27.217, gyro_data=smoothed_gyro_data)
    res = ga.get_acc_direction(sliced_gyro_data)
    print(res)

    # ga.plot_smoothed_gyro_data()
    # ga.find_large_changes(factor=1.1)
    # ga.plot_large_changes()
    # print(ga.formatted_ranges)

    pass