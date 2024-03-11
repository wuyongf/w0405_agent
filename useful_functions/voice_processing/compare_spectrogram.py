import librosa
import librosa.display
import matplotlib.pyplot as plt
import numpy as np

def audio_to_spectrogram(audio_file):
    # Load the audio file
    y, sr = librosa.load(audio_file)
    
    # Generate the spectrogram
    D = librosa.amplitude_to_db(np.abs(librosa.stft(y)), ref=np.max)
    
    # Display the spectrogram
    plt.figure(figsize=(10, 4))
    librosa.display.specshow(D, sr=sr, x_axis='time', y_axis='log')
    plt.colorbar(format='%+2.0f dB')
    plt.title('Spectrogram')
    plt.show()
    
    return D

def compare_spectrograms(spec1, spec2):
    # Calculate the absolute difference between the spectrograms
    diff = np.abs(spec1 - spec2)
    
    # Display the difference spectrogram
    plt.figure(figsize=(10, 4))
    librosa.display.specshow(diff, x_axis='time', y_axis='log')
    plt.colorbar(format='%+2.0f dB')
    plt.title('Difference Spectrogram')
    plt.show()

# Example usage
audio_file1 = "data/demo_voice_slices/door_operation/0_8.wav"  # Replace with the path to your first audio file
audio_file2 = "data/demo_voice_slices/door_operation/0_8.wav"  # Replace with the path to your second audio file

# Convert audio files to spectrograms
spec1 = audio_to_spectrogram(audio_file1)
spec2 = audio_to_spectrogram(audio_file2)

# Compare the spectrograms
compare_spectrograms(spec1, spec2)