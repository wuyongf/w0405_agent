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
    recorder = Recorder()
    try:
        recorder.update_save_path("/home/nw/Desktop/Sounds")
        recorder.start_recording()
    except KeyboardInterrupt:
        recorder.stop_and_save_record()