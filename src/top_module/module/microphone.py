import pyaudio
import wave
import os, time
import threading

class Recorder:
    def __init__(self):
        self.sampling_rate = 44100
        self.n_channels = 1
        self.frames_per_buffer = 1024

        self.audio = pyaudio.PyAudio()

        self.stream = self.audio.open(format=pyaudio.paInt16, 
                                      channels=self.n_channels, 
                                      rate=self.sampling_rate,
                                      input=True,
                                      frames_per_buffer=self.frames_per_buffer)
        self.frames = []
        self.stop_event = threading.Event()

    def update_save_path(self, path):
        self.path = path

    def start_recording(self):
        self.stop_event.clear()
        self.frames = []
        threading.Thread(target=self.thread_recording).start()

    def thread_recording(self):
        while not self.stop_event.is_set():
            try:
                data = self.stream.read(self.frames_per_buffer, exception_on_overflow=False)
                self.frames.append(data)
            except IOError as e:
                # Log or handle the error as needed
                print(f'[microphone.py] e: {e}')
                pass

    def stop_and_save_record(self):
        self.stop_event.set()

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