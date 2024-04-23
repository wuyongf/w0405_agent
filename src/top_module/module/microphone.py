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

        # logic
        self.record_flag = True
        # Use an Event to signal the recording thread to stop
        self.stop_event = threading.Event()

    def update_save_path(self, path):
        self.path = path # "/home/nw/Desktop/Sounds"
        pass
    
    def start_recording(self):
        # Ensure the event is clear at the start of recording
        self.stop_event.clear()
        self.record_flag = True
        self.frames = []  # Ensure frames are cleared before starting
        threading.Thread(target=self.thread_recording).start()

    def thread_recording(self):
        while not self.stop_event.is_set():
            data = self.stream.read(self.frames_per_buffer, exception_on_overflow=False)
            self.frames.append(data)

    def stop_and_save_record(self):
        # Signal the thread to stop
        self.stop_event.set()
        self.record_flag = False

        # Close the PyAudio stream
        self.stream.stop_stream()
        self.stream.close()
        self.audio.terminate()

        file_name = os.path.join(self.path, "recording_" + str(time.time()) + ".wav")
        
        # Save the recording to file
        with wave.open(file_name, "wb") as sound_file:
            sound_file.setnchannels(self.n_channels)
            sound_file.setsampwidth(self.audio.get_sample_size(pyaudio.paInt16))
            sound_file.setframerate(self.sampling_rate)
            sound_file.writeframes(b''.join(self.frames))

        # Clear the frames for the next recording
        self.frames = []

        print(f"Saved: {file_name}")
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