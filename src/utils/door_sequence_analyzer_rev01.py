from src.models.enums.nw import LiftDoorStatus

class DoorSquenceAnalyzer:
    def __init__(self,):
        self.sliced_classes_dir = None
        self.temp_folder_dir = None

        #properties
        self.fps = 15  # Video frames per second
        self.time_per_frame = 1 / self.fps
        
    def set_sliced_classes_dir(self,sliced_classes_dir):
        self.sliced_classes_dir = sliced_classes_dir
        pass

    def set_temp_folder_dir(self,temp_folder_dir):
        self.temp_folder_dir = temp_folder_dir
        pass

    def convert_classids2sliced_statuses(self,):
        # Read the content of the file into a list
        file_path = self.sliced_classes_dir
        with open(file_path, 'r') as file:
            lines = [line.strip() for line in file.readlines()]

        sliced_statuses = []
        # Process each line and determine the status considering adjacent frames
        for i in range(len(lines)):
            # Get current status and adjacent statuses
            current = lines[i].strip('[]')
            previous = lines[i - 1].strip('[]') if i > 0 else ''
            next_status = lines[i + 1].strip('[]') if i < len(lines) - 1 else ''

            # Check for 'Operating' status
            if '2' in current or '2' in previous or '2' in next_status:
                sliced_statuses.append(LiftDoorStatus.Operating)
            # Check for 'FullyClose' status
            elif current == '0':
                sliced_statuses.append(LiftDoorStatus.FullyClose)
            # Check for 'FullyOpen' status
            elif all(s == '1' for s in current.split()):
                sliced_statuses.append(LiftDoorStatus.FullyOpen)
            else:
                sliced_statuses.append(LiftDoorStatus.Unknown)
        return sliced_statuses

    def group_sliced_statuses(self, sliced_statuses):
            compact_statuses_info = []
            start_frame = 0
            current_status = sliced_statuses[0]
            compact_statuses = []

            # Iterate over the statuses to find continuous segments and their durations
            for i, status in enumerate(sliced_statuses[1:], start=1):
                if status != current_status:
                    # Calculate the time duration for the previous segment
                    start_time = start_frame * self.time_per_frame
                    end_time = i * self.time_per_frame
                    compact_statuses_info.append(f"{start_time*2:.1f},{end_time*2:.1f}")
                    # compact_statuses_info.append(f"{start_time:.1f},{end_time:.1f}")
                    compact_statuses.append(current_status)
                    start_frame = i
                    current_status = status

            # Add the last segment
            end_time = len(sliced_statuses) * self.time_per_frame
            compact_statuses_info.append(f"{(start_frame * self.time_per_frame)*2:.1f},{end_time*2:.1f}")
            # compact_statuses_info.append(f"{(start_frame * self.time_per_frame):.1f},{end_time:.1f}")
            compact_statuses.append(current_status)
            return compact_statuses, compact_statuses_info

    def analyze_door_sequence(self, compact_statuses, compact_statuses_info):
        '''
        output:
        1. compact_door_status_info file
        '''
        detailed_statuses = []
        for i in range(len(compact_statuses)):
            prev_item = compact_statuses[i-1] if i > 0 else None
            next_item = compact_statuses[i+1] if i < len(compact_statuses)-1 else None
            current_item = compact_statuses[i]

            if prev_item == None or next_item == None: 
                if LiftDoorStatus.Operating is current_item:
                    detailed_statuses.append(LiftDoorStatus.OperatingUnknown)
                else:
                    detailed_statuses.append(compact_statuses[i])
                continue

            if LiftDoorStatus.Operating is current_item:
                if LiftDoorStatus.FullyOpen is prev_item and LiftDoorStatus.FullyClose is next_item:
                    detailed_statuses.append(LiftDoorStatus.OperatingCloseDoor)
                elif LiftDoorStatus.FullyClose is prev_item and LiftDoorStatus.FullyOpen is next_item:
                    detailed_statuses.append(LiftDoorStatus.OperatingOpenDoor)
                else:
                    detailed_statuses.append(LiftDoorStatus.OperatingUnknown)
            else: detailed_statuses.append(compact_statuses[i])

            # print(f'<debug> compact_statuses: len: {len(compact_statuses)}')
            # print(f'<debug> compact_statuses[31]: {compact_statuses[31]}')
            # print(f'<debug> detailed_statuses: len: {len(detailed_statuses)}')
            # print(f'<debug> compact_statuses_info: len: {len(compact_statuses_info)}')

        compact_door_statuses_info = [[x, list(map(float, y.split(',')))] if isinstance(x, str) else [x.name, list(map(float, y.split(',')))] for x, y in zip(detailed_statuses, compact_statuses_info)]

        output_info = self.merge_rule_rev01(compact_door_statuses_info)

        # Save the results to a file
        output_file_dir = self.temp_folder_dir + 'door_compact_statuses_info.txt'
        with open(output_file_dir, 'w') as output_file:
            for idx, result in enumerate(output_info):
                if(idx is len(output_info)-1): output_file.write(str(result))
                else:output_file.write(str(result) + '\n')

        return output_info, output_file_dir
    
    def merge_rule_rev01(self, statuses_info):
        '''
        if prev and later are 'FullyClose', 'OperatingUnknown' in beteween, merge
        '''
        merged_statuses = []
        i = 0
        while i < len(statuses_info):
            current_status, current_interval = statuses_info[i]
            # Check if current status is 'OperatingUnknown' and can be merged with 'FullyClose'
            if current_status == 'OperatingUnknown':
                can_merge = False
                if i > 0 and i < len(statuses_info) - 1:
                    prev_status, _ = statuses_info[i - 1]
                    next_status, next_interval = statuses_info[i + 1]
                    if prev_status == 'FullyClose' and next_status == 'FullyClose':
                        can_merge = True
                        # Merge current status interval with the next one
                        merged_statuses[-1][1][1] = next_interval[1]
                        i += 1  # Skip the next status as it is merged with the current
                if not can_merge:
                    # If cannot merge, add the current status as is
                    merged_statuses.append([current_status, current_interval])
            else:
                merged_statuses.append([current_status, current_interval])
            i += 1
        return merged_statuses

if __name__ == '__main__':
    # Initialize variables

    dsq = DoorSquenceAnalyzer()
    dsq.set_sliced_classes_dir('data/lift-inspection/temp/20240318/001/door_sliced_classes.txt')
    dsq.set_temp_folder_dir('data/lift-inspection/temp/20240318/001/')

    sliced_statuses = dsq.convert_classids2sliced_statuses()
    compact_statuses, compact_statuses_info = dsq.group_sliced_statuses(sliced_statuses)
    compact_door_statuses_info, door_compact_statuses_info_dir = dsq.analyze_door_sequence(compact_statuses, compact_statuses_info)
    print(door_compact_statuses_info_dir)

    # for item in compact_door_statuses_info:
    #     print(item)
    #     status = item[0]
    #     start_time = item[1][0]
    #     end_time = item[1][1]



