import librosa
import numpy as np
from fastdtw import fastdtw
from scipy.spatial.distance import euclidean
from dtw import dtw

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
        self.listFrames = np.array(list(map(lambda frame: librosa.feature.mfcc(y=frame, sr=self.sampleRate, n_mfcc=n_mfcc),  self.listFrames)))


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
        # x = np.array([2, 0, 1, 1, 2, 4, 2, 1, 2, 0]).reshape(-1, 1)
        # y = np.array([1, 1, 2, 4, 2, 1, 2, 0]).reshape(-1, 1)

        # x = np.array(userFrames)
        x = []
        # x = userFrames.reshape(-1)
        # print(x)
        # print(y)

        # # print(userFrames)
        # y = referenceFrames.reshape(-1)

        for frame in userFrames:
            # print(frame)
            frame = frame.reshape(-1)
            x.append(frame)
            # print(frame)
            # print(userFrames[0])
            # break
        y = []
        for frame in referenceFrames:
            frame = frame.reshape(-1)
            y.append(frame)

        # # print(userFrames)
        # # y = referenceFrames.reshape(-1)
        # manhattan_distance = lambda x, y: np.abs(x - y)

        d, cost_matrix, acc_cost_matrix, path = dtw(x, y, dist=euclidean)

        min = np.min(cost_matrix)
        max = np.max(cost_matrix)

        sum = 0
        for i in range(len(path[0])):
            sum += cost_matrix[path[0][i]][path[1][i]]

        sum /= len(path[0])

        # print(cost_matrix)
        print(1 - (sum - min) / (max - min))



if __name__=='__main__':

    mfccRef = MFCC('/home/dasha/python_diplom/ASR/wavs/training/in_db_sd_low_spl/five-5-0-m.wav')
    mfccRef.calculateMFCC()
    compare = Compare()

    for file in ['/home/dasha/python_diplom/ASR/wavs/training/in_db_sd_low_spl/two-2-0-m.wav', '/home/dasha/python_diplom/ASR/wavs/training/in_db_sd_low_spl/seven-7-0-m.wav', '/home/dasha/python_diplom/ASR/wavs/training/in_db_sd_low_spl/one-1-5-m.wav', '/home/dasha/python_diplom/ASR/wavs/training/in_db_sd_low_spl/five-5-5-m.wav']:
        mfcc1 = MFCC(file)
        print(file.split('/')[-1])
        mfcc1.calculateMFCC()
        compare.crossValidation(mfccRef.listFrames, mfcc1.listFrames)
        print('-'*15)

