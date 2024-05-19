from math import fabs, ceil
from audio import *
from numba import jit
from numba.core.errors import NumbaDeprecationWarning, NumbaPendingDeprecationWarning, NumbaWarning
import warnings

warnings.simplefilter('ignore', category=NumbaDeprecationWarning)
warnings.simplefilter('ignore', category=NumbaPendingDeprecationWarning)
warnings.simplefilter('ignore', category=NumbaWarning)



_SECOND_TO_MILLISECOND = 1000
_GOOD_LOCALITY = 3


class SegmentationWord:

    def __init__(self, audio: Audio) -> None:
        self._audio = audio
        self._mutenessTime = 7 # время - средняя дистанция между словами 50 мс = бред, просто подбираю
        self._sizeWindow = 0 #int(self._mutenessTime * self._audio.sampleRate / _SECOND_TO_MILLISECOND)
        self._thresholdWordSample = 750 # длина, за которую вряд ли что-то скажут

        self.dictSizeWindow = {2.5: (150, 78), 7.5: (200, 80), 15: (200, 87)}

    @jit(cache=True)
    def _calculateThreshold(self, listSample, lenListSample, coefficient = 1.0):   
        return fabs(coefficient * (sum(listSample) / lenListSample))
    

    def _splitWord(self, listSample, sizeWindow, threshold, offset = 0):
        startWordIndex, endWordIndex = 0, 0
        listWordTimeBorders = []
        step = 1

        for i in range (0, len(listSample) - 1, step):
            if (endSlice := i + sizeWindow) >= len(listSample):
                endSlice = len(listSample) - 1
            
            if max(listSample[i:endSlice], default=0) < threshold:
                if endWordIndex - startWordIndex >= self._thresholdWordSample:                  
                    listWordTimeBorders.append((startWordIndex + offset, endWordIndex + offset))
                startWordIndex, endWordIndex = endSlice, endSlice

            endWordIndex = i

        if endWordIndex > startWordIndex:            
            listWordTimeBorders.append((startWordIndex + offset, endWordIndex + offset))
        return listWordTimeBorders


    @jit(cache=True)
    def _splitContinuousWord(self, listSample, sizeWindow, threshold, listWordTimeBorders):
        splitContinuousWord = []
        for time in listWordTimeBorders:
            result = self._splitWord(listSample=listSample[time[0]:time[1]], sizeWindow=sizeWindow, threshold=threshold, offset=time[0])
            if len(result) > 0:
                splitContinuousWord.extend(result)
            else:
                splitContinuousWord.append(time)
        return splitContinuousWord


    @jit(cache=True)
    def _connectWordTime(self, listWordTimeBorders):
        newWordTimeBorder = []
        if len(listWordTimeBorders) == 1:
            if listWordTimeBorders[0][1] - listWordTimeBorders[0][0] >= 150.0:
                return listWordTimeBorders
            else:
                return newWordTimeBorder
            
        i = 1
    
        while i < len(listWordTimeBorders) + 1:

            start, finish = listWordTimeBorders[i - 1][0], listWordTimeBorders[i - 1][1]

            if i != len(listWordTimeBorders):
                while listWordTimeBorders[i][0] - listWordTimeBorders[i - 1][1] <= 50.0:
                    finish = listWordTimeBorders[i][1]
                    i += 1
                    if i >= len(listWordTimeBorders):
                        break
            if finish - start >= 150.0:
                newWordTimeBorder.append((start, finish))
            i += 1
        return newWordTimeBorder



    def searchWordsInAudioFragment(self, start: float, finish: float) -> list:
        """
        На вход: время начало и конца фрагмента в СЕКУНДАХ!!!
        """
        fragment = list(map(lambda x: fabs(x), self._audio.dataNormalizing[int(start * self._audio.sampleRate):ceil(finish * self._audio.sampleRate)]))
        if not fragment:
            return []
        
        difference = finish - start
        duration = list(self.dictSizeWindow.keys())
        duration.insert(0, 0)

        for i in range(len(duration) - 1):
            if duration[i] < difference <= duration[i + 1]:
                sizeWindowSilence, sizeWindowContinuousWord = int(self.dictSizeWindow[duration[i + 1]][0] * self._audio.sampleRate / _SECOND_TO_MILLISECOND), int(self.dictSizeWindow[duration[i + 1]][1] * self._audio.sampleRate / _SECOND_TO_MILLISECOND)
                break

        threshold_1 = self._calculateThreshold(listSample=fragment, lenListSample=len(fragment), coefficient=0.22)
        wordTimeBorders = self._splitWord(listSample=fragment, sizeWindow=sizeWindowSilence, threshold=threshold_1)

        if not wordTimeBorders:
            return wordTimeBorders

        sumSample, lenListWord = 0.0, 0
        for time in wordTimeBorders:
            sumSample += sum(fragment[time[0]:time[1]])
            lenListWord += (time[1] - time[0])

        threshold_2 = self._calculateThreshold(listSample=[sumSample], lenListSample=lenListWord, coefficient=0.4)

        wordTimeBorders = self._splitContinuousWord(fragment, sizeWindowContinuousWord, threshold_2, wordTimeBorders)


        start *= _SECOND_TO_MILLISECOND

        for i, time in enumerate(wordTimeBorders):
            wordTimeBorders[i] = (start + (time[0] * _SECOND_TO_MILLISECOND / self._audio.sampleRate), start + (time[1] * _SECOND_TO_MILLISECOND / self._audio.sampleRate))
        
        # # # График для контроля
        # fig, ax = plt.subplots(figsize=(20,3))
        # ax.plot(fragment)
        # # # plt.show()

        # ax.axhline(y = threshold_2, color='red')
        # ax.axhline(y = threshold_1, color='green')
        # plt.show()
        # print('\n'+'--Time-'*15)
        
        # print(wordTimeBorders)
        
        wordTimeBorders = self._connectWordTime(wordTimeBorders)

        return wordTimeBorders  



    def getWavWord(self, wordTimeBorders, start = 0):
        start *= _SECOND_TO_MILLISECOND
        for time in wordTimeBorders:
                # trimmed_audio = self._audio.audioData[start + (time[0] * _SECOND_TO_MILLISECOND / self._audio.sampleRate):start + (time[1] * _SECOND_TO_MILLISECOND / self._audio.sampleRate)]
                trimmed_audio = self._audio.audioData[int(time[0]):int(time[1])]
                trimmed_audio.export(f"/home/dasha/python_diplom/cut_res/{int(time[0])}:{int(time[1])}.wav", format="wav")



if __name__=='__main__':

    # audio_file = AudioSegment.from_file('/home/dasha/python_diplom/wav/five-in-sentence.wav')
    # start_time =  945.0000000000002  # начало обрезки в миллисекундах
    # end_time = 1830  # конец обрезки в миллисекундах

    # trimmed_audio = audio_file[start_time:end_time]
    # trimmed_audio.export("/home/dasha/python_diplom/cut_res/five-in-sentence-cut.wav", format="wav")


    # search = SearchWord('/home/dasha/python_diplom/wav/five-in-sentence.wav')
    # search = SearchWord('/home/dasha/python_diplom/wav/febn.wav')
    audio = Audio('/home/dasha/python_diplom/wav/user_v.9.wav')
    search = SegmentationWord(audio=audio)
    print(audio.sampleRate)
    


    # bounds = search.searchWordsInAudioFragment(start=0, finish=audio.audioData.duration_seconds, sizeWindowSilence=int(150*audio.sampleRate / _SECOND_TO_MILLISECOND), sizeWindowContinuousWord=int(78*audio.sampleRate / _SECOND_TO_MILLISECOND))
    # bounds = search.searchWordsInAudioFragment(start=0, finish=audio.audioData.duration_seconds)
    #  bounds = search.createSlice(start=0, finish=audio.audioData.duration_seconds, sizeWindowSilence=int(200*audio.sampleRate / _SECOND_TO_MILLISECOND), sizeWindowContinuousWord=int(78*audio.sampleRate / _SECOND_TO_MILLISECOND))
    
    
    # print(f'\n----\nall: {len(bounds)}\n{bounds}')
    
    # search.getWavWord(wordTimeBorders=bounds)

    # for i in range(2, int(audio.audioData.duration_seconds)):

    for time in [(0.0, 1.425), (4.365, 5.415), (7.260000000000001, 8.13), (9.375, 10.155000000000001), (12.000000000000002, 13.005)]:
        print(f'\n---------------------new {time}---------------')
        bounds = search.searchWordsInAudioFragment(start=time[0], finish=time[1])

        # bounds = search.searchWordsInAudioFragment(start=time[0], finish=time[1], sizeWindowSilence=int(150*audio.sampleRate / _SECOND_TO_MILLISECOND), sizeWindowContinuousWord=int(78*audio.sampleRate / _SECOND_TO_MILLISECOND))
        print(f'len {len(bounds)}: time {bounds}')
        search.getWavWord(wordTimeBorders=bounds)


    # bounds = search.searchWordsInAudioFragment(start=2.82, finish=3.735, sizeWindowSilence=int(150*audio.sampleRate / _SECOND_TO_MILLISECOND), sizeWindowContinuousWord=int(78*audio.sampleRate / _SECOND_TO_MILLISECOND))
    # print(f'\n----\n{2.82} to {3.735} sec: {len(bounds)}\n{bounds}')
    # search.getWavWord(wordTimeBorders=bounds)

    # bounds = search.searchWordsInAudioFragment(start=3.9, finish=5.175, sizeWindowSilence=int(150*audio.sampleRate / _SECOND_TO_MILLISECOND), sizeWindowContinuousWord=int(78*audio.sampleRate / _SECOND_TO_MILLISECOND))
    # print(f'\n----\n{3.9} to {5.175} sec: {len(bounds)}\n{bounds}')
    # search.getWavWord(wordTimeBorders=bounds)
    # 
        # if i == 3:
        #     search.getWavWord(wordTimeBorders=bounds)
        #     break


    # search.searchWordsInAudioFragment(945.0, 1830.0)

