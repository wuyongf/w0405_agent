import pyaudio
import wave
import os
import time
import threading

class Recorder:
    def __init__(self, rate=44100, channels=1, frames_per_buffer=1024):
        self.sampling_rate = rate
        self.n_channels = channels
        self.frames_per_buffer = frames_per_buffer
        self.audio = pyaudio.PyAudio()
        self.frames = []
        self.stop_event = threading.Event()
        self.path = None

    def open_stream(self):
        self.stream = self.audio.open(format=pyaudio.paInt16, 
                                      channels=self.n_channels, 
                                      rate=self.sampling_rate,
                                      input=True,
                                      frames_per_buffer=self.frames_per_buffer)

    def close_stream(self):
        self.stream.stop_stream()
        self.stream.close()

    def update_save_path(self, path):
        self.path = path

    def start_recording(self):
        self.stop_event.clear()
        self.frames = []
        self.open_stream()  # Open the stream for a new recording
        threading.Thread(target=self.thread_recording, daemon=True).start()

    def thread_recording(self):
        while not self.stop_event.is_set():
            try:
                data = self.stream.read(self.frames_per_buffer, exception_on_overflow=False)
                self.frames.append(data)
            except IOError as e:
                print(f'[microphone.py] IOError: {e}')

    def stop_and_save_record(self):
        self.stop_event.set()
        while not self.stop_event.is_set():
            time.sleep(0.1)  # Wait for the thread to acknowledge the stop event
        self.close_stream()  # Close the stream properly
        self.audio.terminate()

        file_name = os.path.join(self.path, f"recording_{str(time.time())}.wav")

        with wave.open(file_name, "wb") as sound_file:
            sound_file.setnchannels(self.n_channels)
            sound_file.setsampwidth(self.audio.get_sample_size(pyaudio.paInt16))
            sound_file.setframerate(self.sampling_rate)
            sound_file.writeframes(b''.join(self.frames))

        self.frames = []  # Clear the frames for the next recording

        print(f"Saved: {file_name}")
        return file_name
