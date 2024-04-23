import sounddevice as sd
import soundfile as sf
import os
import time
import threading

class Recorder:
    def __init__(self, rate=44100, channels=1, frames_per_buffer=1024):
        self.sampling_rate = rate
        self.n_channels = channels
        self.frames_per_buffer = frames_per_buffer
        self.frames = []
        self.stop_event = threading.Event()
        self.path = None
        self.device_name = None

    def open_stream(self):
        self.stream = sd.InputStream(
            samplerate=self.sampling_rate,
            channels=self.n_channels,
            callback=self.callback,
            blocksize=self.frames_per_buffer,
            device=self.device_name
        )

    def callback(self, indata, frames, time, status):
        if status:
            print(status, flush=True)
        self.frames.append(indata.copy())

    def close_stream(self):
        self.stream.stop()
        self.stream.close()

    def update_save_path(self, path):
        self.path = path

    def update_input_device(self, device_name):
        self.device_name = device_name

    def start_recording(self):
        self.stop_event.clear()
        self.frames = []
        self.open_stream()  # Open the stream for a new recording
        self.stream.start()

    def stop_and_save_record(self):
        self.stop_event.set()
        self.stream.stop()
        self.stream.close()

        file_name = os.path.join(self.path, f"recording_{str(time.time())}.wav")

        with sf.SoundFile(file_name, mode='w', samplerate=self.sampling_rate, channels=self.n_channels) as sound_file:
            for frame in self.frames:
                sound_file.write(frame)

        self.frames = []  # Clear the frames for the next recording

        print(f"Saved: {file_name}")
        return file_name



if __name__ == '__main__':

    # file_name = os.path.join(self.path, f"recording_{str(time.time())}.wav")
    
    r = Recorder()

    r.update_save_path('data/')
    print(f'1-----')
    r.start_recording()
    time.sleep(10)
    r.stop_and_save_record()   
    print(f'2-----') 
    r.start_recording()
    time.sleep(20)
    r.stop_and_save_record()   
    print(f'3-----') 
    r.start_recording()
    time.sleep(15)
    r.stop_and_save_record()   
    print(f'4-----') 
    r.start_recording()
    time.sleep(25)
    r.stop_and_save_record()   
    print(f'5-----') 
    r.start_recording()
    time.sleep(5)
    r.stop_and_save_record()   
    pass