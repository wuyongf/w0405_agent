import tensorflow_io as tfio
import tensorflow as tf
import cv2
import numpy as np
import os
from pydub import AudioSegment
from scipy import signal
import configparser 


class AudioUtils:
    def __init__(self):
        self.overlap_sec = 1
        pass

    def load_wav_16k_mono(self, filename):
        """Load .wav file and resample to 16k sample rate"""
        # Load encoded wav file
        file_contents = tf.io.read_file(filename)
        # Decode wav (tensors by channels) 
        wav, sample_rate = tf.audio.decode_wav(file_contents, desired_channels=1)
        # Removes trailing axis
        wav = tf.squeeze(wav, axis=-1)
        sample_rate = tf.cast(sample_rate, dtype=tf.int64)
        # Goes from 44100Hz to 16000hz - amplitude of the audio signal
        wav = tfio.audio.resample(wav, rate_in=sample_rate, rate_out=16000)
        return wav

    
    def preprocess(self, file_path, label): 
        """Use STFT to convert data to spectrogram"""
        wav = self.load_wav_16k_mono(file_path)
        # wav = wav[:80000]   # 80000 is the result we determine from the length of the dataset, can change
        
        # Paddling the data shorter than 80000
        # zero_padding = tf.zeros([80000] - tf.shape(wav), dtype=tf.float32)
        # wav = tf.concat([zero_padding, wav],0)
        
        spectrogram = tf.signal.stft(wav, frame_length=320, frame_step=32)
        spectrogram = tf.abs(spectrogram)
        spectrogram = cv2.resize(np.array(spectrogram), (256,256))
        spectrogram = tf.expand_dims(spectrogram, axis=2)
        return spectrogram, label
    
    def highpass_filter(self, y, sr):
        
        filter_stop_freq = 70  # Hz
        filter_pass_freq = 320  # Hz
        filter_order = 5

        nyq = 0.5 * sr
        normal_cutoff = filter_pass_freq / nyq
        b, a = signal.butter(filter_order, normal_cutoff, btype='highpass', analog=False)
        filtered_audio = signal.filtfilt(b, a, y)

        return filtered_audio
    

    def split(self, file_path, file_name, output_dir):
        '''Split audio file into 5-second slices with 1-sec overlap'''
        # Input audio file to be sliced
        # print(file_path)
        # print(output_dir)
        audio = AudioSegment.from_wav(file_path)

        # normalized_sound = self.match_target_amplitude(audio, -30.0)
        # audio = self.highpass_filter(audio,44100)

        # Length of the audiofile in milliseconds
        # n = len(normalized_sound)
        n = len(audio)
        
        # Variable to count the number of sliced chunks
        counter = 1
        
        # Interval length at which to slice the audio file.
        interval = 5 * 1000
        
        # Length of audio to overlap.
        overlap = self.overlap_sec * 1000
        
        # Initialize start and end seconds to 0
        start = 0
        end = 0
        
        # Iterate from 0 to end of the file,
        # with increment = interval
        for i in range(0, 2 * n, interval):
            # During first iteration,
            # start is 0, end is the interval
            if i == 0:
                start = 0
                end = interval
            else:
                start = end - overlap
                end = start + interval
        
            # When end becomes greater than the file length,
            # end is set to the file length
            if end >= n:
                end = n

            if end - start <= 2000: continue
            # Storing audio file from the defined start to end
            # chunk = normalized_sound[start:end]
            chunk = audio[start:end]
        
            # Filename / Path to store the sliced audio
            filename = output_dir + "/" + file_name[:-4] + "_" + str(counter)+"_"+str(start)+"_"+str(end)+'.wav'
        
            # Store the sliced audio file to the defined path
            chunk.export(filename, format ="wav")
            # Print information about the current chunk
            print("Processing chunk "+str(counter)+". Start = "
                                +str(start)+" end = "+str(end))
        
            # Increment counter for the next chunk
            counter = counter + 1

    def match_target_amplitude(self, sound, target_dBFS):
        change_in_dBFS = target_dBFS - sound.dBFS
        return sound.apply_gain(change_in_dBFS)




if __name__ == "__main__":

    file_path = '/home/nw/Documents/GitHub/w0405_agent/data/sounds/Records/20231107/996/recording_1699332347.8895252.wav'
    out_dir = '/home/nw/Documents/GitHub/w0405_agent/data/sounds/Chunk/20231107/996'
    audio = AudioUtils()
    audio.split(file_path, out_dir)

    # config = configparser.ConfigParser()
    # try:
    #     config.read('cfg/config.properties')
    # except:
    #     print("Error loading properties file, check the correct directory")

    # # Example for splitting audio files in the folder
    # # and save to subfolder "chunk"
    
    # for file_name in os.listdir(config.get("RECORDING", 'original_path')):
    #     file_path = os.path.join(config.get("RECORDING", 'original_path'), file_name)
    #     audio = AudioUtils()
    #     audio.split(file_path, config.get("RECORDING", 'chunk_path'))

    # original_path
    # Record/{current_date}/{mission_id}
    # save_path
    # Chunk/{current_date}/{mission_id}

