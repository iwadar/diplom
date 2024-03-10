# import os
from pydub import AudioSegment
# import numpy as np
import matplotlib.pyplot as plt
import sys
from math import fabs

_SECOND_TO_MILLISECOND = 1000


class SearchWord:
    def __init__(self, filename) -> None:
        _wordTime = 200 # время за которое говорят 1 слово - 200 мс
        self.audioData = AudioSegment.from_file(filename)
        self.sampleRate = self.audioData.frame_rate
        self.maxAmplutideInAllSample = 0
        self.initSizeWindow = int(_wordTime * self.sampleRate / _SECOND_TO_MILLISECOND)

        #TODO посмотреть может быть загружать данный таким способом, а не librosa будет быстрее
        # print((np.array(self.audioData.get_array_of_samples(), dtype=np.float32).reshape((-1, self.audioData.channels)) / (
        #     1 << (8 * self.audioData.sample_width - 1)))[-1], self.audioData.frame_rate)
        ###


    def normalization(self, listSample):
        listSample = list(map(lambda sample: sample / self.maxAmplutideInAllSample, listSample))
        return listSample
    

    def calculateThreshold(self, listSample, coefficient = 1.0):            
        self.threshold_1 = coefficient * (sum(listSample) / len(listSample))


    def chunks(self, lst, n):
        """Yield successive n-sized chunks from lst."""
        for i in range(0, len(lst), n):
            chunk = lst[i:i + n]
            yield chunk, max(chunk)


    def checkMutenessUsingTreshold_1(self, listSample):
        splitWord = []
        resultChunks = self.chunks(listSample, self.initSizeWindow)



    def searchWordsInAudioFragment(self, start: float, finish: float):
        fragment = self.audioData[start:finish].get_array_of_samples()
        self.maxAmplutideInAllSample = fabs(max(fragment, key = lambda i: fabs(i), default = 0))
        fragment = self.normalization(fragment)

        self.calculateThreshold(fragment, 0.55)
        self.checkMutenessUsingTreshold_1(fragment)


        # coefficientMillSecondToSize = len(fragment) // (finish - start)
        # print(coefficientMillSecondToSize)

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
        

        # fig, ax = plt.subplots(figsize=(20,3))
        # ax.plot(fragment)
        # plt.show()
        # print(librosa.get_duration(y=self.data, sr=self.sampleRate))





if __name__=='__main__':

    # audio_file = AudioSegment.from_file('/home/dasha/python_diplom/wav/five-in-sentence.wav')
    # start_time =  945.0000000000002  # начало обрезки в миллисекундах
    # end_time = 1830  # конец обрезки в миллисекундах

    # trimmed_audio = audio_file[start_time:end_time]
    # trimmed_audio.export("/home/dasha/python_diplom/cut_res/five-in-sentence-cut.wav", format="wav")


    search = SearchWord('/home/dasha/python_diplom/wav/five-in-sentence.wav')

    search.searchWordsInAudioFragment(945.0, 1830.0)