from datetime import datetime

timestamp = 1709898640.302843
formatted_date = datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')

print("Formatted Date:", formatted_date)

# 516 video-rear 2024-03-08 19:50:40 +                       
#     audio      2024-03-08 19:53:21 - 3:08 = 19:50:13 27    end_time duration   start_time new_duration

#auido_start 15:31:33 audio_end 15:32:57 audio_duration 1:24 
#video_start 15:32:19 video_duration 0:36 video_end 15:32:55
#video_start 15:32:19 video_duration 0:36 video_end 15:32:55
#gyro_start  15:32:19  gyro_duration 0:    gyro_end 15:33:02 
# Formatted Date: 2024-03-08 19:50:40
