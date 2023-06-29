import cv2 as cv
import io
import matplotlib.pyplot as plt
import numpy as np
import pygame
import rpc
import serial
import serial.tools.list_ports
import struct
import os
import time
from PIL import Image

class ThermalCam:
    def __init__(self, port="/dev/ttyACM0", debug=False):
        # Comment the below line if openmv deivce port changed
        self.interface = rpc.rpc_usb_vcp_master(port)
        self.save_folder = "/home/nw/Desktop/Images"
        self.image_path = None
        self.debug = debug

        if not os.path.exists(self.save_folder):
            os.mkdir(self.save_folder)

        # Uncomment the below lines if openmv deivce port changed
        #
        # print("Available Ports:")
        # for port, desc, hwid in serial.tools.list_ports.comports():
        #     print("{} : {} [{}]".format(port, desc, hwid))
        # print("Please enter a port name: ")
        # self.interface = rpc.rpc_usb_vcp_master(port=input())

        if self.debug:
            self.stream_video_in_window()

        # Uncomment the below line to setup your OpenMV Cam for controlling over WiFi.
        #
        # * slave_ip - IP address to connect to.
        # * my_ip - IP address to bind to ("" to bind to all interfaces...)
        # * port - Port to route traffic to.
        #
        # interface = rpc.rpc_network_master(slave_ip="xxx.xxx.xxx.xxx", my_ip="", port=0x1DBA)

    def get_frame_buffer_call_back(self, pixformat_str="sensor.RGB565", framesize_str="sensor.QQVGA", cutthrough=True, silent=True):
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
        pygame.init()

        try:
            screen = pygame.display.set_mode((width, height), flags=pygame.RESIZABLE)
        except TypeError:
            screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("Frame Buffer")
        clock = pygame.time.Clock()

        while(True):
            img = self.get_frame_buffer_call_back()

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
                    image = pygame.image.load(io.BytesIO(img), "jpg")
                    if image is not None:

                        if event.key == pygame.K_d:
                            pygame.image.save(image, os.path.join(self.save_folder, "dry", str(time.time()) + ".jpg"))

                        if event.key == pygame.K_w:
                            pygame.image.save(image, os.path.join(self.save_folder, "wet", str(time.time()) + ".jpg"))

                        if event.key == pygame.K_a:
                            pygame.image.save(image, os.path.join(self.save_folder, "other", str(time.time()) + ".jpg"))

                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()

    def set_save_folder(self, path):
        self.save_folder = path
        if not os.path.exists(self.save_folder):
            os.mkdir(self.save_folder)

    def save_image(self):
        image = self.get_frame_buffer_call_back()
        if image is not None:
            image = Image.open(io.BytesIO(image))
            self.image_path = os.path.join(self.save_folder, str(time.time()) + ".jpg")
            image.save(self.image_path)
            return self.image_path
        else:
            return None
    
    def gray_to_heatmap(self, path):
        colormap = plt.get_cmap('inferno')
        img = cv.imread(path, cv.IMREAD_GRAYSCALE)
        img = (img - img.min()) / (img.max() - img.min())
        heatmap = (colormap(img) * 2**8).astype(np.uint8)[:,:,:3]
        heatmap = cv.cvtColor(heatmap, cv.COLOR_RGB2BGR)
        path = path.replace(".jpg", "_color.jpg")
        cv.imwrite(path, heatmap)
        return path

if __name__ == '__main__':
    camera = ThermalCam(debug=True)