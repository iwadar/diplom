from audio import *
from scipy.spatial.distance import euclidean
from dtw import dtw
import matplotlib.pyplot as plt

import scipy.stats as stats


import os

_ALLOWABLE_ERROR = 20
_STANDART_STEP = 1/8
_VALID_MATCH = 0.5
_INCREASE_STEP = 0.5

directoryWithAudio = '/home/dasha/python_diplom/wav/' 



class MFCC:
    def __init__(self, audio: Audio) -> None:
        self.audio = audio
        self.listFrames = list()
        self.length = 0
        self.data = []

    # def readFile(self):
    #     self.audioData = AudioSegment.from_file(self._fileName)

    #     # self.data, self.sampleRate = librosa.load(self._fileName)
    #     # print(self.data)
    #     # print((np.array(self.audioData.get_array_of_samples(), dtype=np.float32).reshape((-1, self.audioData.channels)) / (
    #     #     1 << (8 * self.audioData.sample_width - 1))), self.audioData.frame_rate)
    #     self.data, self.sampleRate = (np.array(self.audioData.get_array_of_samples(), dtype=np.float32).reshape((-1, self.audioData.channels)) / (
    #         1 << (8 * self.audioData.sample_width - 1))).reshape(-1,), self.audioData.frame_rate
    #     # print(self.data)

    #     print(f'{len(self.data)} <- {len(self.audioData) * self.sampleRate / 1000}')
        
    #     # fig, ax = plt.subplots(figsize=(20,3))
    #     # ax.plot(self.data)
    #     # plt.show()

    #     self.data = nr.reduce_noise(y = self.data, sr=self.sampleRate, stationary=True)
        # self.data = reduced_noise
        # # print(librosa.get_duration(y=self.data, sr=self.sampleRate))


    # def preEmphasis(self):
    #     self.data = librosa.effects.preemphasis(self.data)
        

    def framing(self, length=0.025, shift=0.010):
        # frames = librosa.util.frame(signal, frame_length=frame_length, hop_length=hop_length)
        self.lengthMs = length
        self.shiftMs = shift
        self.length = int(round(self.sampleRate * length))
        shift = int(round(self.sampleRate * shift))

        print(f'Length = {self.length}, shift={shift}')

        for i in range(0, len(self.data), self.length - shift): # я считаю сдвиг должен быть self.length - shift
        
        # for i in range(0, len(data), shift): # я считаю сдвиг должен быть self.length - shift
            frame = self.data[i:i + self.length] # делаем срез

            if len(frame) != self.length: # если не хватает попали на конец данных, забили нулями
                frame = np.pad(frame, (0, (self.length - len(frame))), mode='constant')

            self.listFrames.append(frame)

        self.listFrames = np.array(self.listFrames)

    

    def windowing(self):
        # Эта функция генерирует self.length коэффициентов, на которые нужно умножить каждый элемент в фрейме
        window = np.hamming(self.length)

        self.listFrames = np.array(list(map(lambda frame: frame * window, self.listFrames)))

    def mfcc(self, n_mfcc = 13):
        # Беру 0 массив, потому что не понятно до сих пор как формируется shape результата
        self.listFrames = np.array(list(map(lambda frame: librosa.feature.mfcc(y=frame, sr=self.sampleRate, n_mfcc=n_mfcc, hop_length=self.length).T[0],  self.listFrames)))
        
        # self.listFrames = np.array(list(map(lambda frame: librosa.feature.mfcc(y=frame, sr=self.sampleRate, n_mfcc=n_mfcc,  hop_length=self.length, n_fft=len(self.listFrames)).T[0],  self.listFrames)))
        
        # print(self.listFrames)


    def calculateMFCC(self):
        self.readFile()
        self.preEmphasis()
        self.framing()
        self.windowing()
        self.mfcc()


class Compare:

    """
    ХЕРНЯ ПОКА ЧТО
    """
    def __init__(self) -> None:
        pass
        # вероятно здесь будет какая-то сущность связанная с бд


    
    def crossValidation(self, referenceFrames, userFrames):
        """
        примем пока что они плюс минус равны по размеру
        """
       
        d, cost_matrix, acc_cost_matrix, path = dtw(stats.zscore(userFrames), stats.zscore(referenceFrames), dist=euclidean)

        min = np.min(cost_matrix)
        max = np.max(cost_matrix)

        sum = 0
        for i in range(len(path[0]) - 1):
            sum += cost_matrix[int(path[0][i])][int(path[1][i])]

        sum /= len(path[0])

        # print(1 - (sum - min) / (max - min))
        return (1 - (sum - min) / (max - min))
        # return d    

    def crossValidationLongAudio(self, referenceFrames, userFrames, length, shift):

        index = 0
        sizeReference = len(referenceFrames)
        coefIndexToSec = (length - shift) * 1000

        if abs(len(referenceFrames) - len(userFrames)) <= _ALLOWABLE_ERROR:
            return self.crossValidation(referenceFrames=referenceFrames, userFrames=userFrames), index * coefIndexToSec, (index + sizeReference) * coefIndexToSec
        
        i = 0
        endSlice = 0
        maxMatch = 0.0

        while endSlice < len(userFrames):
            endSlice = i + sizeReference
            if endSlice >= len(userFrames):
                endSlice = len(userFrames)
            if (result := self.crossValidation(referenceFrames=referenceFrames, userFrames=userFrames[i:endSlice])) < _VALID_MATCH:
                i += int(_INCREASE_STEP * sizeReference)
            elif result > maxMatch:              
                maxMatch = result
                index = i
                i += int(_STANDART_STEP * sizeReference)
            else:
                i += int(_STANDART_STEP * sizeReference)

        # вернем отсюда индексы нормализованного массива, а в replaceAudio будем сразу их юзать и не нужны будут доп преобразования
        return maxMatch, index * coefIndexToSec, (index + sizeReference) * coefIndexToSec



if __name__=='__main__':


    mfccRef = MFCC('/home/dasha/python_diplom/ASR/wavs/training/in_db_sd_low_spl/five-5-0-m.wav')
    # mfccRef = MFCC('/home/dasha/python_diplom/wav/hello-dasha.wav')
    # mfccRef = MFCC('/home/dasha/python_diplom/cut_res/five-in-sentence-cut.wav')
    mfccRef.calculateMFCC()
    compare = Compare()

    # for file in ['/home/dasha/python_diplom/ASR/wavs/training/in_db_sd_low_spl/two-2-0-m.wav', '/home/dasha/python_diplom/ASR/wavs/training/in_db_sd_low_spl/seven-7-0-m.wav', '/home/dasha/python_diplom/ASR/wavs/training/in_db_sd_low_spl/one-1-5-m.wav', '/home/dasha/python_diplom/ASR/wavs/training/in_db_sd_low_spl/five-5-5-m.wav']:
    # for file in ['/home/dasha/python_diplom/wav/hello-dasha.wav', '/home/dasha/python_diplom/wav/five-in-sentence.wav', '/home/dasha/python_diplom/wav/one-five.wav', '/home/dasha/python_diplom/wav/no-five.wav',  '/home/dasha/python_diplom/ASR/wavs/training/in_db_sd_low_spl/five-5-0-m.wav', '/home/dasha/python_diplom/ASR/wavs/training/in_db_sd_low_spl/five-5-5-m.wav']:
    print(os.listdir(directoryWithAudio))
    for file in os.listdir(directoryWithAudio):
        mfcc1 = MFCC(directoryWithAudio + file)
        print(file.split('/')[-1])
        mfcc1.calculateMFCC()
        # compare.crossValidation(mfccRef.listFrames, mfcc1.listFrames)
        print(compare.crossValidationLongAudio(mfccRef.listFrames, mfcc1.listFrames, mfcc1.lengthMs, mfcc1.shiftMs))
        print('-'*15)
        # break

