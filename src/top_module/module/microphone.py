import pyaudio
import wave
import os, time
import threading

class Recorder:
    def __init__(self):
        self.sampling_rate = 44100
        self.n_channels = 1 #1
        self.frames_per_buffer = 1024

        self.audio = pyaudio.PyAudio()

        self.stream = self.audio.open(format=pyaudio.paInt16, 
                            # input_device_index=5,
                            channels=self.n_channels, 
                            rate=self.sampling_rate,
                            input=True,
                            frames_per_buffer=self.frames_per_buffer)
        self.frames = []

        # # Get the current default input audio device index
        # default_input_device_index = self.audio.get_default_input_device_info()['index']
        # print(f'default_input_device_index: {default_input_device_index}')

        # rgbcam =  RGBCamRecorder(device_index=0)
        # rgbcam.update_cap_save_path('test')
        # rgbcam.cap_open_cam()
        # rgbcam.cap_rgb_img('test23.jpg')

        # logic
        self.record_flag = True

    def update_save_path(self, path):
        self.path = path # "/home/nw/Desktop/Sounds"
        pass
    
    def start_recording(self):   
        threading.Thread(target=self.thread_recording).start()

    def thread_recording(self):
        while self.record_flag:
            data = self.stream.read(self.frames_per_buffer)
            self.frames.append(data)

    def stop_and_save_record(self):
        self.record_flag = False
        time.sleep(1)
        self.stream.stop_stream()
        self.stream.close()
        self.audio.terminate()
        
        # print(self.path)
        file_name = os.path.join(self.path, "recording_" + str(time.time()) + ".wav")
        
        sound_file = wave.open(file_name, "wb")
        sound_file.setnchannels(self.n_channels)
        sound_file.setsampwidth(self.audio.get_sample_size(pyaudio.paInt16))
        sound_file.setframerate(self.sampling_rate)
        sound_file.writeframes(b''.join(self.frames))
        sound_file.close()

        print("Saved: " + file_name)
        return file_name

if __name__ == "__main__":

    import pyaudio

    p = pyaudio.PyAudio()
    info = p.get_host_api_info_by_index(0)
    numdevices = info.get('deviceCount')

    for i in range(0, numdevices):
        if (p.get_device_info_by_host_api_device_index(0, i).get('maxInputChannels')) > 0:
            print("Input Device id ", i, " - ", p.get_device_info_by_host_api_device_index(0, i).get('name'))


    recorder = Recorder()
    # try:
    #     recorder.update_save_path("/home/nw/Desktop/Sounds")
    #     recorder.start_recording()
    # except KeyboardInterrupt:
    #     recorder.stop_and_save_record()