import numpy as np
import librosa
import noisereduce as nr
from pydub import AudioSegment
import matplotlib.pyplot as plt

class Audio:
    def __init__(self, filename = '') -> None:
        if filename:
            self.audioData = AudioSegment.from_file(filename)
            # print(f'Duration: {self.audioData.duration_seconds}')
            self.dataNormalizing, self.sampleRate = (np.array(self.audioData.get_array_of_samples(), dtype=np.float32).reshape((-1, self.audioData.channels)) / (
                1 << (8 * self.audioData.sample_width - 1))).reshape(-1,), self.audioData.frame_rate
            self.dataNormalizing = nr.reduce_noise(y = self.dataNormalizing, sr=self.sampleRate, stationary=True)
            self.dataNormalizing = librosa.effects.preemphasis(self.dataNormalizing)

        # fig, ax = plt.subplots(figsize=(20,3))
        # ax.plot(self.dataNormalizing)
        # plt.show()

    def updateData(self, filename):
        if filename:
            self.audioData = AudioSegment.from_file(filename)
            # print(f'Duration: {self.audioData.duration_seconds}')
            self.dataNormalizing, self.sampleRate = (np.array(self.audioData.get_array_of_samples(), dtype=np.float32).reshape((-1, self.audioData.channels)) / (
                1 << (8 * self.audioData.sample_width - 1))).reshape(-1,), self.audioData.frame_rate
            self.dataNormalizing = nr.reduce_noise(y = self.dataNormalizing, sr=self.sampleRate, stationary=True)
            self.dataNormalizing = librosa.effects.preemphasis(self.dataNormalizing)
        