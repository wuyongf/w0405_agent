import librosa
import soundfile as sf
import warnings
from pydub import AudioSegment

def convert_wav_to_mp3(wav_file, mp3_file):
    # Load the WAV file
    audio = AudioSegment.from_wav(wav_file)
    
    # Export as MP3
    audio.export(mp3_file, format="mp3")

def slice_audio(audio_file, start_time, end_time, output_file):
    # Suppress warnings
    warnings.filterwarnings("ignore")

    # Load the audio file
    y, sr = librosa.load(audio_file, sr=None)

    # Convert start and end times to sample indices
    start_sample = int(start_time * sr)
    end_sample = int(end_time * sr)

    # Slice the audio
    sliced_audio = y[start_sample:end_sample]

    # Save the sliced audio to a new file
    sf.write(output_file, sliced_audio, sr, 'PCM_24')

# Example usage
audio_file = "data/demo_audio_raw.mp3"  # Replace with the path to your audio file
start_time = 152  # Start time in seconds
end_time = 162  # End time in seconds
output_name = f"result/lift_travelling/{start_time}_{end_time}"  # Path to save the sliced audio
wav_file = output_name + ".wav"

# Slice the audio and extract the desired duration
slice_audio(audio_file, start_time, end_time, wav_file)

# mp3_file = output_name + ".mp3"
# convert_wav_to_mp3(wav_file, mp3_file)