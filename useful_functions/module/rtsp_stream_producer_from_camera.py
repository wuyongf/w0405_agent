# reference: https://www.youtube.com/watch?v=0waGEDZSFQs
# step1: start rtsp-simple-server `docker run --rm -it -e RTSP_PROTOCOLS=tcp -p 8554:8554 aler9/rtsp-simple-server`
# step2: run rtsp_stream_producer_from_camera.py
# step3: run rtsp_stream_consumer.py

import cv2
import subprocess as sp
import numpy as np

rtsp_server = 'rtsp://localhost:8554/mystream'
    
cap = cv2.VideoCapture(0)
sizeStr = str(int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))) + 'x' + str(int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)))
fps = int(cap.get(cv2.CAP_PROP_FPS))
    
command = ['ffmpeg',
            '-re',
            '-s', sizeStr,
            '-r', str(fps),  # rtsp fps (from input server)
            '-i', '-',
            '-pix_fmt', 'yuv420p', # You can change ffmpeg parameter after this item.
            '-r', '30',  # output fps
            '-g', '50',
            '-c:v', 'libx264',
            '-b:v', '2M',
            '-bufsize', '64M',
            '-maxrate', "4M",
            '-preset', 'veryfast',
            '-rtsp_transport', 'tcp',
            '-segment_times', '5',
            '-f', 'rtsp',
            rtsp_server]

command2 = ['ffmpeg',
            '-re',
            '-s', sizeStr,
            '-r', str(fps),  # rtsp fps (from input server) 
            '-i', '-',
            '-pix_fmt', 'yuv420p', # You can change ffmpeg parameter after this item.
            '-tune', 'zerolatency',
            '-c:v', 'libx264',
            '-preset', 'slow',
            '-rtsp_transport', 'tcp',
            '-segment_times', '5', ##?
            '-f', 'rtsp',
            rtsp_server]

process = sp.Popen(command2, stdin=sp.PIPE, shell=True)

while(cap.isOpened()):
    ret, frame = cap.read()
    ret2, frame2 = cv2.imencode('.png', frame)
    process.stdin.write(frame2.tobytes())