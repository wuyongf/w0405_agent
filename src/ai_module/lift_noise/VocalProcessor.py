class VocalProcessor:

    def __init__(self, vocal_files):
        self.vocal_files = vocal_files
        self.intervals = [self.parse_filename_to_interval(filename) for filename in vocal_files]

    @staticmethod
    def parse_filename_to_interval(filename):
        """Parse the filename to extract slice number, start time, and end time,
        and return them as a tuple."""
        parts = filename.split("_")
        slice_number = int(parts[2])
        start_time = int(parts[3])
        end_time = int(parts[4].split(".")[0])
        return (start_time, end_time, slice_number)

    def group_overlapping_intervals(self):
        """Group overlapping intervals and return consolidated groups."""
        intervals = sorted(self.intervals)  # Sort by start time
        grouped_intervals = []
        current_group = [intervals[0]]

        for i in range(1, len(intervals)):
            _, current_end, _ = current_group[-1]
            next_start, next_end, next_slice = intervals[i]

            if current_end >= next_start:  # Overlap
                current_group.append((next_start, next_end, next_slice))
            else:
                grouped_intervals.append(current_group)
                current_group = [(next_start, next_end, next_slice)]

        grouped_intervals.append(current_group)  # Add the last group
        return grouped_intervals

    def format_grouped_intervals(self, grouped_intervals):
        """Format the grouped intervals for output."""
        output = []
        group_number = 1
        for group in grouped_intervals:
            start_time = group[0][0]
            end_time = max(end for _, end, _ in group)
            slice_numbers = [str(slice_num) for _, _, slice_num in group]
            slice_count = len(group)

            # output.append(f"# {group_number} start_time: {start_time}, end_time: {end_time}, "
            #               f"no. of files: {slice_count}, slice number: {', '.join(slice_numbers)}")
            
            output.append(f"{group_number},{start_time},{end_time}")
            
            group_number += 1

        return "\n".join(output)


# Example usage
vocal = [
    "recording_1699332347.8895252_5_16000_21000.wav", 
    "recording_1699332347.8895252_8_28000_33000.wav",
    "recording_1699332347.8895252_15_56000_60163.wav", 
    "recording_1699332347.8895252_4_12000_17000.wav",
    "recording_1699332347.8895252_14_52000_57000.wav", 
    "recording_1699332347.8895252_3_8000_13000.wav",
    "recording_1699332347.8895252_1_0_5000.wav", 
    "recording_1699332347.8895252_13_48000_53000.wav",
    "recording_1699332347.8895252_6_20000_25000.wav"
]

processor = VocalProcessor(vocal)
grouped_intervals = processor.group_overlapping_intervals()
formatted_output = processor.format_grouped_intervals(grouped_intervals)
print(formatted_output)
