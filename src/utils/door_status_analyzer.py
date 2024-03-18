import os
import cv2
from ultralytics import YOLO
import supervision as sv
import numpy as np
from src.models.enums.nw import CameraPosition
from src.utils.door_sequence_analyzer_rev01 import DoorSquenceAnalyzer

class DoorStatusAnalyzer:
    def __init__(self,):
        self.model_ckpt_dir = None
        self.temp_folder_dir = None
        self.preprocess_folder_dir = None
        self.camera_position = CameraPosition.Null

        #logic
        self.detect_list = None
        
        #door_sequence_analyzer
        self.dsq = DoorSquenceAnalyzer()

    def set_ckpt(self, model_ckpt_dir):
        self.model_ckpt_dir = model_ckpt_dir

    def set_source_video(self, source_video_dir):
        self.source_video_dir = source_video_dir

    def set_temp_folder_dir(self, temp_folder_dir):
        self.temp_folder_dir = temp_folder_dir
        self.dsq.set_temp_folder_dir(temp_folder_dir)

    def set_preprocess_folder_dir(self, preprocess_folder_dir):
        self.preprocess_folder_dir = preprocess_folder_dir
        os.makedirs(self.preprocess_folder_dir, exist_ok=True)

    def set_camera_position(self, camera_position: CameraPosition):
        self.camera_position = camera_position
        pass

    def yolov8_detect_door_status(self, ):
        '''
        return:
        1. predicted_video_dir
        2. predicted_video_frames_dir
        output:
        1. predicted_video
        2. predicted_video_frames
        3. detected_door_class_list
        '''

        box_annotator = sv.BoxAnnotator(
            thickness=2,
            text_thickness=1,
            text_scale=0.5
        )

        # Load a custom trained model
        model = YOLO(self.model_ckpt_dir)

        # Initialize VideoWriter
        fourcc = cv2.VideoWriter_fourcc(*'MJPG')

        predicted_video_name = None
        match(self.camera_position):
            case CameraPosition.Front:
                predicted_video_name = 'predicted_' + 'front' + '_video.avi'
            case CameraPosition.Rear:
                predicted_video_name = 'predicted_' + 'rear' + '_video.avi'
            case _:
                predicted_video_name = 'predicted_' + 'null' + '_video.avi'

        predicted_video_dir = os.path.join(self.preprocess_folder_dir, predicted_video_name)
        out = cv2.VideoWriter(predicted_video_dir, fourcc, 15.0, (1280, 720))  # Adjust FPS and frame size as needed

        # Logging
        self.detect_list = []

        # Perform tracking with the model
        for idx, result in enumerate(model.track(source=self.source_video_dir, show=False, stream=False, save = False)): 
            frame = result.orig_img
            detections = sv.Detections.from_yolov8(result)

            # print(f'<debug> detections.idx:   {idx}')
            # print(f'<debug> detections.class_id:   {detections.class_id}')
            # print(f'<debug> detections.confidence: {detections.confidence}')
            # # print(f'<debug> detections.tracker_id: {detections.tracker_id}') # Useless
            # print(f'<debug> detections.xyxy:       {detections.xyxy}')

            self.detect_list.append(detections.class_id)
            
            labels = [
                f" {model.names[d[2]]} {d[1]:.2f}" #{d.tracker_id}
                for d in detections
            ]
            
            frame = box_annotator.annotate(scene=frame, detections=detections, labels=labels)
            
            # Write the frame to video
            out.write(frame)

            # Save the frame as image
            predicted_video_frames_dir = None
            match(self.camera_position):
                case CameraPosition.Front:
                    predicted_video_frames_dir = 'predicted-' + 'front' + '-video-frames'
                case CameraPosition.Rear:
                    predicted_video_frames_dir = 'predicted-' + 'rear' + '-video-frames'
                case _:
                    predicted_video_frames_dir = 'predicted-' + 'null' + '-video-frames'

            predicted_video_frames_dir = os.path.join(self.temp_folder_dir, predicted_video_frames_dir)
            os.makedirs(predicted_video_frames_dir, exist_ok =True)
            resized_frame = cv2.resize(frame, (160, 120))  # Reduce Image Size.
            rotated_frame = cv2.rotate(resized_frame, cv2.ROTATE_90_CLOCKWISE) # Rotate the frame by 90 degrees clockwise
            file_name = "{:05d}".format(idx)+".jpg"
            cv2.imwrite(os.path.join(predicted_video_frames_dir, file_name), rotated_frame)   

        # Release everything when job is finished
        out.release()

        # Write detected door status list
        door_sliced_classes_dir = self.temp_folder_dir  +'door_sliced_classes.txt'
        with open(door_sliced_classes_dir, 'w') as f:
            for line in self.detect_list:
                f.write(f"{line}\n")

        return predicted_video_dir, predicted_video_frames_dir, door_sliced_classes_dir

    def analyse(self,):
        
        pass


if __name__ == "__main__":
    
    dsa = DoorStatusAnalyzer()
    dsa.set_ckpt('../ai_module/door_status/ckpt/best.pt')
    dsa.set_preprocess_folder_dir('data/lift-inspection/preprocess/'+ '20240318/001/')
    dsa.set_temp_folder_dir('data/lift-inspection/temp/'+ '20240318/001/')
    dsa.set_source_video("data/lift-inspection/raw-data/20240318/001/rear_video_1709898640.608474.avi")
    dsa.set_camera_position(CameraPosition.Rear)

    predicted_video_dir, predicted_video_frames_dir, door_sliced_classes_dir = dsa.yolov8_detect_door_status()

    dsa.dsq.set_sliced_classes_dir(door_sliced_classes_dir)
    sliced_statuses = dsa.dsq.convert_classids2sliced_statuses()
    compact_statuses, compact_statuses_info = dsa.dsq.group_sliced_statuses(sliced_statuses)
    compact_door_statuses_info, door_compact_statuses_info_dir = dsa.dsq.analyze_door_sequence(compact_statuses, compact_statuses_info)
    print(door_compact_statuses_info_dir)

    

