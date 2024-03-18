from pydub import AudioSegment

def get_audio_duration(audio_path):
    audio = AudioSegment.from_file(audio_path)
    duration_sec = len(audio) / 1000  # Duration in seconds
    return duration_sec

def trim_audio(audio_path, start_time, end_time):
    audio = AudioSegment.from_file(audio_path)
    start_ms = start_time * 1000
    end_ms = end_time * 1000
    trimmed_audio = audio[start_ms:end_ms]  # Trim the audio between start and end times
    trimmed_audio.export('trimmed_audio.wav', format='wav')  # Export the trimmed audio to a new file

def convert_to_mp3(audio_path):
    audio = AudioSegment.from_file(audio_path)
    audio.export('converted_audio.mp3', format='mp3')  # Export the audio to MP3 format

def convert_to_stereo_audio(audio_path):
    audio = AudioSegment.from_file(audio_path)
    if audio.channels == 1:
        print("Audio already has 1 channel")
    else:
        audio = audio.set_channels(1)  # Convert stereo audio to mono
        audio.export('mono_audio.wav', format='wav')
        print("Audio channels converted to mono")

def convert_to_mono_audio(audio_path):
    audio = AudioSegment.from_file(audio_path)
    if audio.channels == 2:
        audio = audio.set_channels(1)  # Convert stereo audio to mono
        audio.export('mono_audio.wav', format='wav')
        print("Audio converted to mono")
    else:
        print("Audio already has 1 channel")



# Example usage:
audio_path = 'data/recording_1709898801.1256263.wav'
duration_sec = get_audio_duration(audio_path)
if duration_sec is not None:
    print(f"Audio duration: {duration_sec:.2f} seconds")

# Trim the audio file from 10 to 20 seconds
start_time = 10
end_time = 20
trim_audio(audio_path, start_time, end_time)
print(f"Audio trimmed from {start_time} to {end_time} seconds")

# Convert the trimmed audio to MP3 format
convert_to_mp3('trimmed_audio.wav')
print("Trimmed audio converted to MP3 format")

# Convert the audio to mono if it's stereo
convert_to_mono_audio('trimmed_audio.wav')