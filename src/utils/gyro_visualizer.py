import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import savgol_filter
import ast

## workflow
def algin_gyro_with_timestampe(descrete_gyro_data):
    # Prepare the dataset
    timestamps = np.array([item[1] for item in descrete_gyro_data])
    gyro_data = np.concatenate([item[0] for item in descrete_gyro_data])

    # Assuming that gyro data is collected at regular intervals, compute time array
    time_array = np.linspace(0, timestamps[-1], len(gyro_data))

    return time_array, gyro_data

def smmoth_gyro_data(raw_gyro_data):
    '''Smooth the data using Savitzky-Golay filter'''
    # smoothed_gyro_data = savgol_filter(gyro_data, window_length=51, polyorder=3)
    smoothed_gyro_data = savgol_filter(raw_gyro_data, window_length=81, polyorder=7)
    return smoothed_gyro_data

def cal_slope(x_array, y_array):
    # Calculate the mean of the x-values and y-values
    mean_x = np.mean(x_array)
    mean_y = np.mean(y_array)

    # Calculate the slope of the line using linear regression formula
    numerator = np.sum((x_array - mean_x) * (y_array - mean_y))
    denominator = np.sum((x_array - mean_x) ** 2)
    slope = numerator / denominator

    print("Slope of the line:", slope)
    return slope

def slice_gyro_data(time_array, start_sec, end_sec, gyro_data):
    # Find the indices corresponding to the start and end times
    start_index = np.argmax(time_array >= start_sec)
    end_index = np.argmax(time_array >= end_sec)

    return time_array[start_index:end_index], gyro_data[start_index:end_index]

def get_acc_direction(gyro_duration_data):
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

def load_gyro_compact_info(file_dir):
    # Load data
    with open(file_dir, 'r') as f:
        lines = f.readlines()

    descrete_gyro_data = [[list(map(float, ast.literal_eval(item)[0].split(','))), float(ast.literal_eval(item)[1])] for item in lines]
    return descrete_gyro_data

# gyro_compact_info_dir = 'gyro_compact_info.txt'
gyro_compact_info_dir = 'gyro_compact_info_531.txt'
descrete_gyro_data = load_gyro_compact_info(gyro_compact_info_dir)
print(descrete_gyro_data)

# Program Start
time_array, gyro_data = algin_gyro_with_timestampe(descrete_gyro_data)

smoothed_gyro_data = smmoth_gyro_data(gyro_data)

# sliced_time_arr, sliced_gyro_arr  = slice_gyro_data(time_array, start_sec = 7, end_sec = 21, gyro_data = smoothed_gyro_data)
sliced_time_arr, sliced_gyro_arr  = slice_gyro_data(time_array, start_sec = 9.382, end_sec = 27.217, gyro_data = smoothed_gyro_data)

res = get_acc_direction(sliced_gyro_arr)
print(res)

###----------------------------------------------------------------
def group_timestamps(timestamps, max_gap=5):
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

def format_grouped_ranges(grouped_ranges):
    formatted_list = []
    for start, end in grouped_ranges:
        # Calculate the length of the range, assuming integer seconds
        length = int(end) - int(start) + 1
        formatted_list.append([length, start, end])
    return formatted_list

# Identify indices where lift is likely travelling, characterized by large changes in acceleration
# Threshold for derivative might need adjusting based on the specifics of the data

gyro_derivative = np.gradient(smoothed_gyro_data)
threshold = np.std(gyro_derivative)/1.1  # Example threshold based on standard deviation
travelling_indices = np.where(abs(gyro_derivative) > threshold)[0]
print(time_array[travelling_indices])

# Group the timestamps into ranges
grouped_ranges = group_timestamps(time_array[travelling_indices])

# Format the grouped ranges
formatted_ranges = format_grouped_ranges(grouped_ranges)

print(formatted_ranges)
print(len(formatted_ranges))

# 'formatted_ranges' will be your final list containing the grouped durations
# Plot the curve (if needed)
plt.figure(figsize=(10, 6))
plt.plot(np.arange(len(gyro_data)), gyro_data, label='Original', alpha=0.5)
plt.plot(np.arange(len(smoothed_gyro_data)), smoothed_gyro_data, label='Smoothed', linewidth=2)
plt.xlabel('Time (frames)')
plt.ylabel('Gyro Data')
plt.title('Gyro Data Smoothing')
plt.legend()
plt.show()

# Plot the gyro_derivative curve(if needed)
plt.figure(figsize=(10, 6))
plt.plot(np.arange(len(gyro_derivative)), gyro_derivative, label='gyro_derivative', alpha=0.5)
plt.xlabel('Time (frames)')  
plt.ylabel('Gyro Data')
plt.title('gyro_derivative')  
plt.legend()
plt.show()

# Plot large changes if needed
plt.figure(figsize=(14, 7))
plt.plot(time_array, gyro_data, label='Original', alpha=0.5)
plt.plot(time_array, smoothed_gyro_data, label='Smoothed', linewidth=2)
plt.scatter(time_array[travelling_indices], smoothed_gyro_data[travelling_indices], color='red', label='Lift Travelling')
plt.xlabel('Time (sec)')
plt.ylabel('Gyro Data')
plt.title('Lift Travelling Range Detection')
plt.legend()
plt.show()

# # Plot the specific range of smoothed_gyro_data
# plt.figure(figsize=(10, 6))
# plt.plot(time_array[start_index:end_index], smoothed_gyro_data[start_index:end_index], label='Smoothed', linewidth=2)
# plt.xlabel('Time (sec)')
# plt.ylabel('Gyro Data')
# plt.title('Smoothed Gyro Data for Specific Time Range')
# plt.legend()
# plt.grid(True)
# plt.show()