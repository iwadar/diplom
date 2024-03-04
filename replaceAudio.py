# import os
from pydub import AudioSegment
# import numpy as np
import matplotlib.pyplot as plt
import sys


class SearchWord:
    def __init__(self, filename) -> None:
        self.audioData = AudioSegment.from_file(filename)


        #TODO посмотреть может быть загружать данный таким способом, а не librosa будет быстрее
        # print((np.array(self.audioData.get_array_of_samples(), dtype=np.float32).reshape((-1, self.audioData.channels)) / (
        #     1 << (8 * self.audioData.sample_width - 1)))[-1], self.audioData.frame_rate)
        ###

        self.sizeWindow = 25 # Я считаю что люди говорят слово за 25 миллисекунд
        self.offset = 10


    def searchWordsInAudioFragment(self, start: float, finish: float):
        fragment = self.audioData[start:finish].get_array_of_samples()

        coefficientMillSecondToSize = len(fragment) // (finish - start)
        print(coefficientMillSecondToSize)

        # length = coefficientMillSecondToSize * self.sizeWindow
        # shift = coefficientMillSecondToSize * self.offset

        # minAmplitude = sys.maxsize
        # indexEnd = 0
        # for i in range (0, len(fragment) - 1, length - shift):
        #     frame = fragment[i:length]
        #     if (_ := min(frame)) < minAmplitude:
        #         minAmplitude = _
        #         indexEnd = frame.index(_)






        # return 
        

        fig, ax = plt.subplots(figsize=(20,3))
        ax.plot(fragment)
        plt.show()
        # print(librosa.get_duration(y=self.data, sr=self.sampleRate))



if __name__=='__main__':

    # audio_file = AudioSegment.from_file('/home/dasha/python_diplom/wav/five-in-sentence.wav')
    # start_time =  945.0000000000002  # начало обрезки в миллисекундах
    # end_time = 1830  # конец обрезки в миллисекундах

    # trimmed_audio = audio_file[start_time:end_time]
    # trimmed_audio.export("/home/dasha/python_diplom/cut_res/five-in-sentence-cut.wav", format="wav")


    search = SearchWord('/home/dasha/python_diplom/wav/five-in-sentence.wav')

    search.searchWordsInAudioFragment(945.0, 1830.0)