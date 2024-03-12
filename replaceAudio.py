# import os
from pydub import AudioSegment
# import numpy as np
import matplotlib.pyplot as plt
import sys
from math import fabs
import noisereduce as nr


_SECOND_TO_MILLISECOND = 1000


class SearchWord:
    def __init__(self, filename) -> None:
        _wordTime = 2 # время за которое говорят 1 слово - 200 мс
        self.audioData = AudioSegment.from_file(filename)
        self.sampleRate = self.audioData.frame_rate
        self.maxAmplutideInAllSample = 0
        self.sizeWindow = int(_wordTime * self.sampleRate / _SECOND_TO_MILLISECOND)
        self.threshold_1 = 0
        self.threshold_2 = 0


        #TODO посмотреть может быть загружать данный таким способом, а не librosa будет быстрее
        # print((np.array(self.audioData.get_array_of_samples(), dtype=np.float32).reshape((-1, self.audioData.channels)) / (
        #     1 << (8 * self.audioData.sample_width - 1)))[-1], self.audioData.frame_rate)
        ###


    def normalization(self, listSample):
        # превратили все в значения по модулю
        listSample = list(map(lambda sample: fabs(sample / self.maxAmplutideInAllSample), listSample))
        # listSample = list(map(lambda sample: sample / self.maxAmplutideInAllSample, listSample))
        return listSample
    

    def calculateThreshold(self, listSample, coefficient = 1.0):   
            # return fabs(coefficient * (sum(listSample) / len(listSample)))
        return fabs(coefficient * (sum(listSample) / len(listSample)))
    

    def splitWord(self, lst, n, threshold):
        startWordIndex = 0
        endWordIndex = 0
        splitWord = []
        self.sizeWindow = sys.maxsize

        for i in range (0, len(lst), 1):
            if (endSlice := i + n) == len(lst) + 2:
                break
            
            if max(lst[i:endSlice], key = lambda i: fabs(i), default = 0) < threshold:
                if (difference := endWordIndex - startWordIndex) >= n * 10:
                    print(f'{n * 10}, {startWordIndex} : {endWordIndex}')
                    splitWord.append({(startWordIndex * _SECOND_TO_MILLISECOND / self.sampleRate , endWordIndex* _SECOND_TO_MILLISECOND / self.sampleRate): lst[startWordIndex:endWordIndex]})
                    if difference < self.sizeWindow:
                        self.sizeWindow = difference
                startWordIndex, endWordIndex = i, i
            else:
                endWordIndex = i
        return splitWord



    # def checkMutenessUsingTreshold_1(self, listSample):
    #     splitWord = []
    #     for word in self.splitWord(listSample, self.initSizeWindow, self.threshold_1):
    #         splitWord.extend(word)
    #     fig, ax = plt.subplots(figsize=(20,3))
    #     ax.plot(splitWord)
    #     # ax.axhline(y = self.threshold_1, color='red')
    #     plt.show()
        # return splitWord




    def searchWordsInAudioFragment(self, start: float, finish: float):
        fragment = self.audioData[start:finish].get_array_of_samples()
        # fragment = nr.reduce_noise(y = fragment, sr=self.sampleRate, stationary=True)

        self.maxAmplutideInAllSample = fabs(max(fragment, key = lambda i: fabs(i), default = 0))
        fragment = self.normalization(fragment)

        # fig, ax = plt.subplots(figsize=(20,3))
        # ax.plot(fragment)
        # plt.show()

        self.threshold_1 = self.calculateThreshold(fragment, 0.55)
        self.threshold_2 = self.calculateThreshold(fragment)
        self.splitWords = self.splitWord(fragment, self.sizeWindow, self.threshold_1)
        # fragment = self.checkMutenessUsingTreshold_2(fragment)


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
        # ax.axhline(y = self.threshold_1, color='red')
        # plt.show()
        # print(librosa.get_duration(y=self.data, sr=self.sampleRate))


    def getWavWord(self, start):
        i = 0
        for word in self.splitWords:

            for time in word:

                trimmed_audio = self.audioData[start + time[0]:start + time[1]]
                trimmed_audio.export(f"/home/dasha/python_diplom/cut_res/{i}.wav", format="wav")
                i += 1





if __name__=='__main__':

    # audio_file = AudioSegment.from_file('/home/dasha/python_diplom/wav/five-in-sentence.wav')
    # start_time =  945.0000000000002  # начало обрезки в миллисекундах
    # end_time = 1830  # конец обрезки в миллисекундах

    # trimmed_audio = audio_file[start_time:end_time]
    # trimmed_audio.export("/home/dasha/python_diplom/cut_res/five-in-sentence-cut.wav", format="wav")


    search = SearchWord('/home/dasha/python_diplom/wav/five-in-sentence.wav')

    search.searchWordsInAudioFragment(945.0, 1830.0)
    search.getWavWord(945.0)
