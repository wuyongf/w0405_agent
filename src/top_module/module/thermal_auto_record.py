import cv2
import numpy as np
import rpc
import struct
import os
import time
from datetime import datetime, timedelta

class ThermalCam:
    def __init__(self, port="/dev/ttyACM0", debug=False):
        # Uncomment the below lines if openmv deivce port changed
        #
        # import serial.tools.list_ports
        # print("Available Ports:")
        # for port, desc, hwid in serial.tools.list_ports.comports():
        #     print("{} : {} [{}]".format(port, desc, hwid))
        # port = input("Please enter a port name: ")

        self.interface = rpc.rpc_usb_vcp_master(port)
        self.image_path = None
        self.debug = debug

        if self.debug:
            self.stream_video_in_window()

        # Uncomment the below line to setup your OpenMV Cam for controlling over WiFi.
        #
        # * slave_ip - IP address to connect to.
        # * my_ip - IP address to bind to ("" to bind to all interfaces...)
        # * port - Port to route traffic to.
        #
        # interface = rpc.rpc_network_master(slave_ip="xxx.xxx.xxx.xxx", my_ip="", port=0x1DBA)

    def __get_frame_buffer_call_back(self, pixformat_str="sensor.RGB565", framesize_str="sensor.QQVGA", cutthrough=True, silent=True):
        if not silent: print("Getting Remote Frame...")

        result = self.interface.call("jpeg_image_snapshot", "%s,%s" % (pixformat_str, framesize_str))
        if result is not None:

            size = struct.unpack("<I", result)[0]
            img = bytearray(size)

            if cutthrough:
                # Fast cutthrough data transfer with no error checking.

                # Before starting the cut through data transfer we need to sync both the master and the
                # slave device. On return both devices are in sync.
                result = self.interface.call("jpeg_image_read")
                if result is not None:

                    # GET BYTES NEEDS TO EXECUTE NEXT IMMEDIATELY WITH LITTLE DELAY NEXT.

                    # Read all the image data in one very large transfer.
                    self.interface.get_bytes(img, 5000) # timeout

            else:
                # Slower data transfer with error checking.

                # Transfer 32 KB chunks.
                chunk_size = (1 << 15)

                if not silent: print("Reading %d bytes..." % size)
                for i in range(0, size, chunk_size):
                    ok = False
                    for j in range(3): # Try up to 3 times.
                        result = self.interface.call("jpeg_image_read", struct.pack("<II", i, chunk_size))
                        if result is not None:
                            img[i:i+chunk_size] = result # Write the image data.
                            if not silent: print("%.2f%%" % ((i * 100) / size))
                            ok = True
                            break
                        if not silent: print("Retrying... %d/2" % (j + 1))
                    if not ok:
                        if not silent: print("Error!")
                        return None

            return img

        else:
            if not silent: print("Failed to get Remote Frame!")

        return None

    def stream_video_in_window(self, width=640, height=480):
        import pygame
        import io

        pygame.init()

        try:
            screen = pygame.display.set_mode((width, height), flags=pygame.RESIZABLE)
        except TypeError:
            screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("Frame Buffer")
        clock = pygame.time.Clock()

        while(True):
            img = self.__get_frame_buffer_call_back()

            if img is not None:
                try:
                    screen.blit(pygame.transform.scale(pygame.image.load(io.BytesIO(img), "jpg"), (width, height)), (0, 0))
                    pygame.display.update()
                    clock.tick()
                except pygame.error:
                    continue

            print(clock.get_fps())

            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    try:
                        image = pygame.image.load(io.BytesIO(img), "jpg")
                    except pygame.error:
                        continue

                    filename = time.strftime("%Y%m%d %H.%M.%S", time.localtime()) + " gray.jpg"

                    if event.key == pygame.K_d:
                        pygame.image.save(image, os.path.join(self.save_folder, "dry", filename))

                    if event.key == pygame.K_w:
                        pygame.image.save(image, os.path.join(self.save_folder, "wet", filename))

                    if event.key == pygame.K_a:
                        pygame.image.save(image, os.path.join(self.save_folder, "other", filename))

                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()

    def set_save_folder(self, path):
        if not os.path.exists(path):
            print("Please make sure the directory exists for saving thermal image data.")
        else:
            datestring = time.strftime("%Y%m%d", time.localtime())
            self.save_folder = os.path.join(path, datestring)
            os.makedirs(self.save_folder, exist_ok=True)

            if self.debug:
                os.makedirs(os.path.join(self.save_folder, "dry"), exist_ok=True)
                os.makedirs(os.path.join(self.save_folder, "wet"), exist_ok=True)
                os.makedirs(os.path.join(self.save_folder, "other"), exist_ok=True)

    def capture_image(self):
        image = self.__get_frame_buffer_call_back()
        if image is not None:
            filename = time.strftime("%Y%m%d %H.%M.%S", time.localtime()) + " gray.jpg"
            filepath = os.path.join(self.save_folder, filename)

            image = np.asarray(image, dtype="uint8")
            image = cv2.imdecode(image, cv2.IMREAD_GRAYSCALE)
            cv2.imwrite(filepath, image)
            return filepath
        else:
            return None
    
    def gray_to_heatmap(self, filepath):
        gray = cv2.imread(filepath, cv2.IMREAD_GRAYSCALE)
        cv2.normalize(gray, gray, 0, 255, cv2.NORM_MINMAX)
        heatmap = cv2.applyColorMap(gray, cv2.COLORMAP_INFERNO)

        filepath = filepath.replace("gray", "rainbow")
        cv2.imwrite(filepath, heatmap)
        return filepath

if __name__ == '__main__':
    camera = ThermalCam(debug=False)
    camera.set_save_folder("/home/nw/Desktop/Images")

    # Init
    interval_min = 1 #s

    # start_time_hour = 18
    # start_time_min  = 16


    # Define the interval in seconds (30 minutes)
    interval_seconds = interval_min #* 60

    # Define the start time (18:05)
    # start_time = datetime.now().replace(hour=start_time_hour, minute=start_time_min, second=0, microsecond=0)
    start_time = datetime.now()
    current_time = datetime.now()

    # # Calculate the time difference to the next trigger time
    # time_difference = start_time - current_time
    # if time_difference.total_seconds() < 0:
    #     pass
    #     # start_time += timedelta(days=1)
    # print(f'sleep 5s...')
    # time.sleep(5)
    print(f'start...')

    # Loop to trigger the method
    while True:

        current_time = datetime.now()
        time_difference = start_time - current_time

        if time_difference.total_seconds() <= 0:
            print("Capture the image at", current_time)
            # Call your method here
            camera.capture_image()

            # Update the start_time for the next interval
            start_time += timedelta(seconds=interval_seconds)
            print("Next capture time at", start_time)

        # Sleep for a short duration to avoid high CPU usage
        time.sleep(1)

