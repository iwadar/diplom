import torch
import time
import os
from TTS.api import TTS
from pydub import AudioSegment



_START_MUTENESS = 0.09
_END_MUTENESS = 0.83
_MILLISECOND = 1000
# Get device
# device = "cuda" if torch.cuda.is_available() else "cpu"

# # # Init TTS
# tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2").to(device)

# # Run TTS
# # ❗ Since this model is multi-lingual voice cloning model, we must set the target speaker_wav and language
# # Text to speech list of amplitude values as output
# wav = tts.tts(text="Привет, мир!", speaker_wav="/home/dasha/python_diplom/wav/user_v.10.wav", language="ru")

# print(type(wav))

class GeneratorAudio:
    def __init__(self, language='ru', speaker = '') -> None:
        device = "cuda" if torch.cuda.is_available() else "cpu"
        self.tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2").to(device)
        self.speaker = speaker
        self.language = language
        self.filePath = os.getcwd() + '/temp_wav/'
        os.makedirs(self.filePath, mode=0o777, exist_ok=True)
    
    def generateWord(self, text):
        word = None
        fileName = self.filePath + f"{text + str(time.time())}.wav"
        if self.speaker:
            self.tts.tts_to_file(text=text, speaker_wav=self.speaker, language=self.language, file_path=fileName)
            word = AudioSegment.from_file(fileName)
            word = word[word.duration_seconds * _MILLISECOND * _START_MUTENESS:word.duration_seconds * _MILLISECOND * _END_MUTENESS]
            os.remove(fileName)
        return word
