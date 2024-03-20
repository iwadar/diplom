# import os
# from pydub import AudioSegment
# import numpy as np
# import matplotlib.pyplot as plt
# import sys
from math import fabs, ceil
from audio import *

_SECOND_TO_MILLISECOND = 1000


class SegmentationWord:
    # def __init__(self, filename) -> None:
    #     _mutenessTime = 5 # время - средняя дистанция между словами 50 мс = бред просто подбираю
    #     self._audioData = AudioSegment.from_file(filename)
    #     self.sampleRate = self._audioData.frame_rate
    #     self.maxAmplutideInAllSample = 0
    #     self._sizeWindow = int(_mutenessTime * self.sampleRate / _SECOND_TO_MILLISECOND)
    #     self.threshold_1 = 0
    #     self.threshold_2 = 0

    def __init__(self, audio: Audio) -> None:
        self._audio = audio
        self._mutenessTime = 5 # время - средняя дистанция между словами 50 мс = бред, просто подбираю
        self._sizeWindow = 0#int(self._mutenessTime * self._audio.sampleRate / _SECOND_TO_MILLISECOND)
        # self.threshold_1 = 0
        # self.threshold_2 = 0


    # def normalization(self, listSample):
    #     # превратили все в значения по модулю
    #     listSample = list(map(lambda sample: fabs(sample / self.maxAmplutideInAllSample), listSample))
    #     return listSample
    

    def _calculateThreshold(self, listSample, lenListSample, coefficient = 1.0):   
        return fabs(coefficient * (sum(listSample) / lenListSample))
    

    def _splitWord(self, listSample, sizeWindow, threshold, offset = 0):
        startWordIndex = 0
        endWordIndex = 0
        listWordTimeBorders = []
        step = 1
        # print(sizeWindow)
        for i in range (0, len(listSample), step):
            endSlice = i + sizeWindow
            if max(listSample[i:endSlice]) < threshold:
                if endWordIndex - startWordIndex >= sizeWindow * 10:
                    print(f'{startWordIndex + offset} : {endWordIndex + offset}')
                    listWordTimeBorders.append((startWordIndex + offset, endWordIndex + offset))
                startWordIndex = endSlice
            endWordIndex = endSlice
        # print(listWordTimeBorders)

        if endWordIndex - startWordIndex >= sizeWindow * 10:
            listWordTimeBorders.append((startWordIndex + offset, endWordIndex + offset))
            # print(f'{startWordIndex + offset} : {endWordIndex + offset}')
        # print(listWordTimeBorders)
        return listWordTimeBorders


    def _splitContinuousWord(self, listSample, sizeWindow, threshold, listWordTimeBorders):
        splitContinuousWord = []
        print('-'*20)
        for time in listWordTimeBorders:
            # word = listSample[time[0]:time[1]]
            # fig, ax = plt.subplots(figsize=(20,3))
            # ax.plot(word)
            # ax.axhline(y = threshold, color='red')
            # plt.show()
            # print((time[1] - time[0]))

            # надо чекать что слово разбилось и тогда удалять, если не разбилось тогда оставлять 
            # result = self._splitWord(listSample=listSample[time[0]:time[1]], sizeWindow=int((time[1] - time[0]) * 0.01), threshold=threshold, offset=time[0])
            
            result = self._splitWord(listSample=listSample[time[0]:time[1]], sizeWindow=sizeWindow, threshold=threshold, offset=time[0])
            if len(result) > 0:
                splitContinuousWord.extend(result)
            else:
                splitContinuousWord.append(time)
        return splitContinuousWord




    # def _searchWordsInAudioFragment(self, start: float, finish: float):
    #     """
    #     начальная функция, принимает на вход время и выделяет кусок, нормализует и т.д.
    #     """
    #     fragment = self._audioData[start:finish].get_array_of_samples()
    #     # sys.exit()

    #     # fragment = nr.reduce_noise(y = fragment, sr=self.sampleRate, stationary=True)

    #     self.maxAmplutideInAllSample = fabs(max(fragment, key = lambda i: fabs(i), default = 0))
    #     fragment = self.normalization(fragment)
    #     print(fragment)
    #     self.threshold_1 = self._calculateThreshold(listSample=fragment, lenListSample=len(fragment), coefficient=0.47)

    #     # fig, ax = plt.subplots(figsize=(20,3))
    #     # ax.plot(fragment)
    #     # ax.axhline(y = self.threshold_1, color='red')
    #     # plt.show()

    #     # fig, ax = plt.subplots(figsize=(20,3))
    #     # ax.plot(fragment)
    #     # plt.show()

    #     self.wordTimeBorders = self.splitWord(fragment, self._sizeWindow, self.threshold_1)

    #     sumSample, lenListWord = 0.0, 0

    #     for time in self.wordTimeBorders:
    #         sumSample += sum(fragment[time[0]:time[1]])
    #         lenListWord += time[1] - time[0]

    #     self.threshold_2 = self._calculateThreshold(listSample=[sumSample], lenListSample=lenListWord)

    #     self.wordTimeBorders = self._splitContinuousWord(fragment, self._sizeWindow * 2, self.threshold_2, self.wordTimeBorders)        

    #     fig, ax = plt.subplots(figsize=(20,3))
    #     ax.plot(fragment)
    #     ax.axhline(y = self.threshold_2, color='red')
    #     ax.axhline(y = self.threshold_1, color='green')

    #     plt.show()
    #     # print(librosa.get_duration(y=self.data, sr=self.sampleRate))


    def searchWordsInAudioFragment(self, start: float, finish: float) -> list:
        """
        На вход: время начало и конца фрагмента в СЕКУНДАХ!!!
        """
        self._sizeWindow = int(self._mutenessTime * self._audio.sampleRate / _SECOND_TO_MILLISECOND)
        fragment = list(map(lambda x: fabs(x), self._audio.dataNormalizing[int(start * self._audio.sampleRate):ceil(finish * self._audio.sampleRate)]))
        threshold_1 = self._calculateThreshold(listSample=fragment, lenListSample=len(fragment), coefficient=0.47)
        wordTimeBorders = self._splitWord(fragment, self._sizeWindow, threshold_1)

        sumSample, lenListWord = 0.0, 0

        for time in wordTimeBorders:
            sumSample += sum(fragment[time[0]:time[1]])
            lenListWord += time[1] - time[0]

        threshold_2 = self._calculateThreshold(listSample=[sumSample], lenListSample=lenListWord)

        wordTimeBorders = self._splitContinuousWord(fragment, ceil(self._sizeWindow * 2.5), threshold_2, wordTimeBorders)

        start *= _SECOND_TO_MILLISECOND

        # print(f'now {wordTimeBorders}')
        # # # График для контроля
        # fig, ax = plt.subplots(figsize=(20,3))
        # ax.plot(self._audio.dataNormalizing)
        # ax.axhline(y = threshold_2, color='red')
        # ax.axhline(y = threshold_1, color='green')
        # plt.show()
        for i, time in enumerate(wordTimeBorders):
            # print(f'ready: {time}')
            wordTimeBorders[i] = (start + (time[0] * _SECOND_TO_MILLISECOND / self._audio.sampleRate), start + (time[1] * _SECOND_TO_MILLISECOND / self._audio.sampleRate))

        return wordTimeBorders  



    def getWavWord(self, wordTimeBorders, start = 0):
        i = 0

        start *= _SECOND_TO_MILLISECOND
        for time in wordTimeBorders:
                trimmed_audio = self._audio.audioData[start + (time[0] * _SECOND_TO_MILLISECOND / self._audio.sampleRate):start + (time[1] * _SECOND_TO_MILLISECOND / self._audio.sampleRate)]
                trimmed_audio.export(f"/home/dasha/python_diplom/cut_res/{time[0]}:{time[1]}.wav", format="wav")
                i += 1





if __name__=='__main__':

    # audio_file = AudioSegment.from_file('/home/dasha/python_diplom/wav/five-in-sentence.wav')
    # start_time =  945.0000000000002  # начало обрезки в миллисекундах
    # end_time = 1830  # конец обрезки в миллисекундах

    # trimmed_audio = audio_file[start_time:end_time]
    # trimmed_audio.export("/home/dasha/python_diplom/cut_res/five-in-sentence-cut.wav", format="wav")


    # search = SearchWord('/home/dasha/python_diplom/wav/five-in-sentence.wav')
    # search = SearchWord('/home/dasha/python_diplom/wav/febn.wav')
    audio = Audio('/home/dasha/python_diplom/wav/many-five.wav')
    search = SegmentationWord(audio=audio)

    bounds = search.searchWordsInAudioFragment(start=2.31, finish=3.93)
    print(bounds)
    # search.searchWordsInAudioFragment(0, -1)


    # search.searchWordsInAudioFragment(945.0, 1830.0)
    # search.getWavWord(start=1.26, wordTimeBorders=bounds)
