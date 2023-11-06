from gtts import gTTS
import subprocess

import gtts.lang
print(gtts.lang.tts_langs())


# Define the sentences in English, Cantonese, and Chinese
sentences = {
    'en': "Our robot is currently using the elevator. We appreciate your patience.",
    'cantonese': "機械人正在使用電梯，請耐心等候。",
    'zh-CN': "机器人正在使用电梯，请耐心等待。"
}

# Iterate through the sentences and generate TTS audio for each
for lang, sentence in sentences.items():
    tts = gTTS(sentence, lang=lang)
    tts.save(f'tts_{lang}.mp3')

# Play the audio files using aplay
for lang in sentences.keys():
    subprocess.call(['aplay', f'tts_{lang}.mp3'])