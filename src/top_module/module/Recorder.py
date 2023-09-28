import pyaudio
import wave
import os, time

class Recorder:
    def __init__(self):
        self.sampling_rate = 44100
        self.n_channels = 1
        self.frames_per_buffer = 1024
        self.path = "/home/nw/Desktop/Sounds"

        self.audio = pyaudio.PyAudio()

        self.stream = self.audio.open(format=pyaudio.paInt16, 
                            channels=self.n_channels, 
                            rate=self.sampling_rate,
                            input=True,
                            frames_per_buffer=self.frames_per_buffer)
        self.frames = []

    def start_recording(self):   
        while True:
            data = self.stream.read(self.frames_per_buffer)
            self.frames.append(data)
   

    def save_record(self):
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

        print("Saved" + file_name)

if __name__ == "__main__":
    recorder = Recorder()
    try:
        recorder.start_recording()
    except KeyboardInterrupt:
        recorder.save_record()