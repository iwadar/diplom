import torch
from TTS.api import TTS
from pydub import AudioSegment

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
        self.filePath = '/home/dasha/python_diplom/temp_wav/'
    
    
    def generateWord(self, text):
        word = None
        fileName = self.filePath + f"{text}.wav"
        if self.speaker:
            # word = self.tts.tts(text=text, speaker_wav=self.speaker, language=self.language)
            self.tts.tts_to_file(text=text, speaker_wav=self.speaker, language=self.language, file_path=fileName)
            word = AudioSegment.from_file(fileName)
            
        return word
