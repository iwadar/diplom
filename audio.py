import numpy as np
import librosa
import noisereduce as nr
from pydub import AudioSegment
from math import isclose

_STANDART_SAMPLE_RATE = 22050

class Audio:
    def __init__(self, filename = '') -> None:
        self.updateData(filename=filename)


    def updateData(self, filename):
        if filename:
            self.audioData = AudioSegment.from_file(filename)
            if self.audioData.set_frame_rate != _STANDART_SAMPLE_RATE:
                self.audioData = self.audioData.set_frame_rate(_STANDART_SAMPLE_RATE)
            self.dataNormalizing, self.sampleRate = (np.array(self.audioData.get_array_of_samples(), dtype=np.float32).reshape((-1, self.audioData.channels)) / (
                1 << (8 * self.audioData.sample_width - 1))).reshape(-1,), self.audioData.frame_rate
            if not isclose(len(self.dataNormalizing) / self.sampleRate, self.audioData.duration_seconds):
                print('[ERROR]: Sample rate conversion error')
                self.dataNormalizing, self.sampleRate, self.audioData = [], None, None
            else:
                self.dataNormalizing = nr.reduce_noise(y = self.dataNormalizing, sr=self.sampleRate, stationary=True)
                self.dataNormalizing = librosa.effects.preemphasis(self.dataNormalizing)