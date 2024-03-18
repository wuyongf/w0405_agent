import os
import numpy as np
from pathlib import Path
import src.utils.repet as repet
from pydub import AudioSegment
import wave

class AudioTool:
    def __init__(self,):
        self.save_folder = None
        pass

    def set_save_folder_dir(self, dir):
        self.save_folder = dir

    def get_audio_duration(self, audio_dir):
        audio = AudioSegment.from_file(audio_dir)
        duration_sec = len(audio) / 1000  # Duration in seconds
        return duration_sec

    def trim_audio(self, audio_dir, start_sec, end_sec):
        audio = AudioSegment.from_file(audio_dir)
        start_ms = start_sec * 1000
        end_ms = end_sec * 1000
        trimmed_audio = audio[start_ms:end_ms]  # Trim the audio between start and end times
        trimmed_audio_file_dir = os.path.join(self.save_folder, 'trimmed_audio.wav')
        trimmed_audio.export(trimmed_audio_file_dir, format='wav')  # Export the trimmed audio to a new file
        return trimmed_audio_file_dir

    def convert_to_mp3(self, audio_dir):
        audio = AudioSegment.from_file(audio_dir)
        mp3_file_dir = os.path.join(self.save_folder, 'converted_audio.mp3')
        audio.export(mp3_file_dir, format='mp3')  # Export the audio to MP3 format
        return mp3_file_dir
        
    def convert_to_mono_audio(self, input_file_dir):
        with wave.open(input_file_dir, 'rb') as wav:
            num_frames = wav.getnframes()
            frame_rate = wav.getframerate()
            num_channels = wav.getnchannels()

            # Read audio data
            audio_data = wav.readframes(num_frames)

        # Convert bytes to numpy array of integers
        audio_data = np.frombuffer(audio_data, dtype=np.int16)

        # Reshape the stereo audio data to separate channels
        audio_data = audio_data.reshape(-1, num_channels)

        # Average across channels to convert to mono
        audio_mono = np.mean(audio_data, axis=1).astype(np.int16)

        # Write mono audio to a new file
        output_file_dir = os.path.join(self.save_folder, 'mono_audio.wav')
        with wave.open(output_file_dir, 'wb') as wav_out:
            wav_out.setnchannels(1)
            wav_out.setsampwidth(wav.getsampwidth())
            wav_out.setframerate(frame_rate)
            wav_out.writeframes(audio_mono.tobytes())

        return output_file_dir
        
    def convert_to_stereo_audio(self, input_file_dir):
        with wave.open(input_file_dir, 'rb') as wav:
            num_frames = wav.getnframes()
            frame_rate = wav.getframerate()
            num_channels = wav.getnchannels()

            # Read mono audio data
            audio_data = wav.readframes(num_frames)

        # Convert bytes to numpy array of integers
        audio_data = np.frombuffer(audio_data, dtype=np.int16)

        # Reshape the mono audio data to create a stereo effect
        audio_stereo = np.column_stack((audio_data, audio_data))

        # Write stereo audio to a new file
        stereo_audio_dir = os.path.join(self.save_folder, 'stereo_audio.wav')
        with wave.open(stereo_audio_dir, 'wb') as wav_out:
            wav_out.setnchannels(2)  # Stereo
            wav_out.setsampwidth(wav.getsampwidth())
            wav_out.setframerate(frame_rate)
            wav_out.writeframes(audio_stereo.tobytes())
        
        return stereo_audio_dir

    def separate_audio(self, stereo_audio_dir):
        '''
        need stereo audio
        '''
        # Read the audio signal (normalized) with its sampling frequency in Hz
        audio_signal, sampling_frequency = repet.wavread(stereo_audio_dir)

        # Estimate the background signal, and the foreground signal
        background_signal = repet.extended(audio_signal, sampling_frequency)
        foreground_signal = audio_signal - background_signal

        # Write the background and foreground signals
        background_file_dir = os.path.join(self.save_folder, "background_signal.wav")
        foreground_file_dir = os.path.join(self.save_folder, "foreground_signal.wav")
        repet.wavwrite(background_signal, sampling_frequency, background_file_dir)
        repet.wavwrite(foreground_signal, sampling_frequency, foreground_file_dir)

        return foreground_file_dir, background_file_dir

if __name__ == '__main__':

    audio_tool = AudioTool()
    audio_tool.set_save_folder_dir('result')

    raw_audio_dir = "data/recording_1709898801.1256263.wav"

    res = audio_tool.get_audio_duration(raw_audio_dir)
    print(res)

    trimmed_audio_dir = audio_tool.trim_audio(raw_audio_dir, start_sec=2, end_sec=20)
    print(trimmed_audio_dir)

    stereo_audio_dir = audio_tool.convert_to_stereo_audio(trimmed_audio_dir)
    print(stereo_audio_dir)

    foreground_file_dir, _ = audio_tool.separate_audio(stereo_audio_dir)
    print(foreground_file_dir)

    mono_audio_dir = audio_tool.convert_to_mono_audio(foreground_file_dir)
    print(mono_audio_dir) # mono_audio will be used for model training and inference

    res = audio_tool.convert_to_mp3(mono_audio_dir) # mp3 file will be uploaded to cloud
    print(res)

    pass