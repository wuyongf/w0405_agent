import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import savgol_filter
import ast

# Load data
with open('gyro_compact_info.txt', 'r') as f:
    lines = f.readlines()

for item in lines:
    item_list = ast.literal_eval(item)[0]
    print(item_list[0])

data = [[list(map(float, ast.literal_eval(item)[0].split(','))), float(ast.literal_eval(item)[1])] for item in lines]

# Prepare the dataset
timestamps = np.array([item[1] for item in data])
gyro_data = np.concatenate([item[0] for item in data])

# Assuming that gyro data is collected at regular intervals, compute time array
time_array = np.linspace(0, timestamps[-1], len(gyro_data))

#---------------------------------------------------------------------------------------------------------

# Smooth the data using Savitzky-Golay filter
# smoothed_gyro_data = savgol_filter(gyro_data, window_length=51, polyorder=3)
smoothed_gyro_data = savgol_filter(gyro_data, window_length=81, polyorder=7)

# Plot the curve
plt.figure(figsize=(10, 6))
plt.plot(np.arange(len(gyro_data)), gyro_data, label='Original', alpha=0.5)
plt.plot(np.arange(len(smoothed_gyro_data)), smoothed_gyro_data, label='Smoothed', linewidth=2)
plt.xlabel('Time (frames)')
plt.ylabel('Gyro Data')
plt.title('Gyro Data Smoothing')
plt.legend()
plt.show()

# Compute the first derivative of the smoothed data
gyro_derivative = np.gradient(smoothed_gyro_data)

# Plot the curve
plt.figure(figsize=(10, 6))

# plt.plot(np.arange(len(smoothed_gyro_data)), smoothed_gyro_data, label='Smoothed', linewidth=2)
plt.plot(np.arange(len(gyro_derivative)), gyro_derivative, label='gyro_derivative', alpha=0.5)
plt.xlabel('Time (frames)')
plt.ylabel('Gyro Data')
plt.title('gyro_derivative')
plt.legend()
plt.show()

# Identify indices where lift is likely travelling, characterized by large changes in acceleration
# Threshold for derivative might need adjusting based on the specifics of the data
threshold = np.std(gyro_derivative)/1.1  # Example threshold based on standard deviation
travelling_indices = np.where(abs(gyro_derivative) > threshold)[0]

# Plot the results
import matplotlib.pyplot as plt

plt.figure(figsize=(14, 7))
plt.plot(time_array, gyro_data, label='Original', alpha=0.5)
plt.plot(time_array, smoothed_gyro_data, label='Smoothed', linewidth=2)
plt.scatter(time_array[travelling_indices], smoothed_gyro_data[travelling_indices], color='red', label='Lift Travelling')
plt.xlabel('Time (sec)')
plt.ylabel('Gyro Data')
plt.title('Lift Travelling Range Detection')
plt.legend()
plt.show()


print(time_array[travelling_indices])

########==========================================================

# Define the start and end times (replace these with your desired values)
start_time = 10  # Example start time in seconds
end_time = 20    # Example end time in seconds

# Find the indices corresponding to the start and end times
start_index = np.argmax(time_array >= start_time)
end_index = np.argmax(time_array >= end_time)

# Plot the specific range of smoothed_gyro_data
plt.figure(figsize=(10, 6))
plt.plot(time_array[start_index:end_index], smoothed_gyro_data[start_index:end_index], label='Smoothed', linewidth=2)
plt.xlabel('Time (sec)')
plt.ylabel('Gyro Data')
plt.title('Smoothed Gyro Data for Specific Time Range')
plt.legend()
plt.grid(True)
plt.show()
########==========================================================

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

# # Replace 'file_path' with the path to your text file
# file_path = 'gyro_compact_info.txt'

# # Read the timestamps from the file and sort them
# with open(file_path, 'r') as file:
#     timestamps = sorted([float(line.strip()) for line in file])

# Group the timestamps into ranges
grouped_ranges = group_timestamps(time_array[travelling_indices])

# Format the grouped ranges
formatted_ranges = format_grouped_ranges(grouped_ranges)

print(formatted_ranges)
print(len(formatted_ranges))

# 'formatted_ranges' will be your final list containing the grouped durations
###----------------------------------------------------------------

# Note: This code is an example and the threshold for determining lift travelling may need to be adjusted. 
# The 'travelling_indices' array can be further processed to determine continuous ranges of lift travel.

#----------------------------------------------------------------------------------------------------------------------------

# # Smooth the data using Savitzky-Golay filter
# smoothed_gyro_data = savgol_filter(gyro_data, window_length=51, polyorder=3)

# # Compute the first derivative of the smoothed data
# gyro_derivative = np.gradient(smoothed_gyro_data)

# # Define a threshold for considering significant changes (this will need to be tuned for your data)
# threshold = np.std(gyro_derivative) / 1.1

# # Identify where significant changes occur
# significant_changes = np.abs(gyro_derivative) > threshold

# # Now, find continuous ranges where significant changes are True
# travel_durations = []
# start = None
# for i, significant in enumerate(significant_changes):
#     if significant and start is None:
#         start = i  # Start of a new range
#     elif not significant and start is not None:
#         end = i  # End of a range
#         travel_durations.append((time_array[start], time_array[end - 1]))
#         start = None
# # Check if the last range goes till the end
# if start is not None:
#     travel_durations.append((time_array[start], time_array[-1]))

# print(travel_durations)

# travel_durations now contains tuples of start and end times for each travelling duration