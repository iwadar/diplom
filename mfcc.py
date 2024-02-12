import librosa
import numpy as np
from scipy.spatial.distance import euclidean
from dtw import dtw

_ALLOWABLE_ERROR = 20
_STANDART_STEP = 1
_VALID_MATCH = 0.5
_INCREASE_STEP = 2

class MFCC:
    def __init__(self, fileName) -> None:
        self._fileName = fileName
        self.data = None
        self.sampleRate = 0
        self.listFrames = list()
        self.length = 0

    def readFile(self):
        self.data, self.sampleRate = librosa.load(self._fileName)


    def preEmphasis(self):
        self.data = librosa.effects.preemphasis(self.data)
        

    def framing(self, length=0.025, shift=0.010):
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
       
        d, cost_matrix, acc_cost_matrix, path = dtw(userFrames, referenceFrames, dist=euclidean)

        min = np.min(cost_matrix)
        max = np.max(cost_matrix)

        sum = 0
        for i in range(len(path[0]) - 1):
            sum += cost_matrix[int(path[0][i])][int(path[1][i])]

        sum /= len(path[0])

        # print(cost_matrix)
        # print(1 - (sum - min) / (max - min))
        return (1 - (sum - min) / (max - min))

    def crossValidationLongAudio(self, referenceFrames, userFrames):

        if abs(len(referenceFrames) - len(userFrames)) <= _ALLOWABLE_ERROR:
            return self.crossValidation(referenceFrames=referenceFrames, userFrames=userFrames)
        
        i = 0
        maxMatch = 0.0
        index = 0
        sizeReference = len(referenceFrames)
        while i != len(userFrames):
            endSlice = i + sizeReference
            if endSlice >= len(userFrames):
                endSlice = len(userFrames)
            if (result := self.crossValidation(referenceFrames=referenceFrames, userFrames=userFrames[i:endSlice])) < _VALID_MATCH:
                i += _INCREASE_STEP
            elif result > maxMatch:
                maxMatch = result
                index = i
                i += _STANDART_STEP
            else:
                i += _STANDART_STEP
        # print({maxMatch}')
        return maxMatch, index



if __name__=='__main__':

    mfccRef = MFCC('/home/dasha/python_diplom/ASR/wavs/training/in_db_sd_low_spl/five-5-0-m.wav')
    mfccRef.calculateMFCC()
    compare = Compare()

    # for file in ['/home/dasha/python_diplom/ASR/wavs/training/in_db_sd_low_spl/two-2-0-m.wav', '/home/dasha/python_diplom/ASR/wavs/training/in_db_sd_low_spl/seven-7-0-m.wav', '/home/dasha/python_diplom/ASR/wavs/training/in_db_sd_low_spl/one-1-5-m.wav', '/home/dasha/python_diplom/ASR/wavs/training/in_db_sd_low_spl/five-5-5-m.wav']:
    for file in ['/home/dasha/python_diplom/wav/one-five.wav', '/home/dasha/python_diplom/wav/no-five.wav']:
        mfcc1 = MFCC(file)
        print(file.split('/')[-1])
        mfcc1.calculateMFCC()
        print(compare.crossValidationLongAudio(mfccRef.listFrames, mfcc1.listFrames))
        print('-'*15)
        # break

