from audio import *
from scipy.spatial.distance import euclidean, cosine
from dtw import dtw
from math import ceil
# import matplotlib.pyplot as plt

import scipy.stats as stats

_ALLOWABLE_ERROR = 20
_STANDART_STEP = 1/16
_VALID_MATCH = 0.5
_INCREASE_STEP = 0.5

_WORD_PRESENCE_TRESHOLDER = 2
_ALLOWED_ERROR_FLOAT = 0.01

directoryWithAudio = '/home/dasha/python_diplom/wav/'



class MFCC:
    def __init__(self, audio: Audio) -> None:
        self.audio = audio
        self.listFrames = list()
        self.length = 0
        

    def framing(self, length=0.025, shift=0.010):
        # frames = librosa.util.frame(signal, frame_length=frame_length, hop_length=hop_length)
        self.lengthMs = length
        self.shiftMs = shift
        self.length = int(round(self.audio.sampleRate * length))
        shift = int(round(self.audio.sampleRate * shift))

        # print(f'Length = {self.length}, shift={shift}')

        for i in range(0, len(self.audio.dataNormalizing), self.length - shift): # я считаю сдвиг должен быть self.length - shift
        
        # for i in range(0, len(data), shift): # я считаю сдвиг должен быть self.length - shift
            frame = self.audio.dataNormalizing[i:i + self.length] # делаем срез

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
        self.listFrames = np.array(list(map(lambda frame: librosa.feature.mfcc(y=frame, sr=self.audio.sampleRate, n_mfcc=n_mfcc, hop_length=self.length).T[0],  self.listFrames)))
        # self.listFrames = stats.zscore(self.listFrames)
        # print(self.listFrames.shape)
        # self.listFrames = np.array(list(map(lambda frame: librosa.feature.mfcc(y=frame, sr=self.audio.sampleRate, n_mfcc=n_mfcc,  hop_length=self.length, n_fft=len(self.listFrames)).T[0],  self.listFrames)))
        
        # print(self.listFrames)


    def calculateMFCC(self):
        if len(self.listFrames):
            self.listFrames = list(self.listFrames).clear()
            self.listFrames = []
        # self.readFile()
        # self.preEmphasis()
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
        ИЗНАЧАЛЬНАЯ ФУНКЦИЯ
        примем пока что они плюс минус равны по размеру
        """

        # userFrames, referenceFrames = stats.zscore(userFrames), stats.zscore(referenceFrames)

        if np.isnan(userFrames).any() or np.isinf(userFrames).any():
            return -1
    
        for item in referenceFrames:
            if np.isnan(item).any() or np.isinf(item).any():
                return -1

        _, cost_matrix, _, path = dtw(userFrames, referenceFrames, dist=euclidean)

        # cost_matrix = stats.zscore(cost_matrix)

        if np.isnan(cost_matrix).any() or np.isinf(cost_matrix).any():
            return -1

        min, max, sum = np.min(cost_matrix), np.max(cost_matrix), 0.0

        for i in range(len(path[0]) - 1):
            sum += cost_matrix[int(path[0][i])][int(path[1][i])]

        sum /= len(path[0])

        return (1 - ((sum - min) / (max - min)))
    

    def _crossValidation(self, referenceFrames, userFrames):
        userFrames = stats.zscore(userFrames)

        if np.isnan(userFrames).any() or np.isinf(userFrames).any():
            return -1
    
        averageResult = 0.0
        for ref in referenceFrames: # (mfcc, weight)
            reference, weight = ref[0], ref[1]
            
            if np.isnan(reference).any() or np.isinf(reference).any():
                return -1

            _, cost_matrix, _, path = dtw(userFrames, reference, dist=euclidean)

            if np.isnan(cost_matrix).any() or np.isinf(cost_matrix).any():
                return -1

            min, max, sum = np.min(cost_matrix), np.max(cost_matrix), 0.0

            for i in range(len(path[0]) - 1):
                sum += cost_matrix[int(path[0][i])][int(path[1][i])]

            sum /= len(path[0])

            # print(f'value : {(1 - ((sum - min) / (max - min)))}')

            averageResult += (1 - ((sum - min) / (max - min))) * weight


        return averageResult
    

    def crossValidationLongAudio(self, referenceFrames, userFrames, coefIndexToSec):
        """
        На вход: referenceFrames - список из списков MFCC коэффициентов
        """

        index, listTimeInterval = 0, []

        sizeReference = 0

        for ref in referenceFrames:
            # print(len(ref[0]))
            # if len(ref) > sizeReference:
            #     sizeReference = len(ref)
            sizeReference += len(ref[0])

        sizeReference = int(sizeReference / len(referenceFrames))

        print(sizeReference)

        i, rating, count = 0, 0.0, 0
        startIndex, endIndex = 0, 0

        maxRes = 0.0

        while i < len(userFrames):
            endSlice = i + sizeReference
            # print(f'i = {i}, end = {endSlice}')

            result = self._crossValidation(referenceFrames=referenceFrames, userFrames=userFrames[i:endSlice])

    # РАСКОММЕНТИТЬ
            if result > maxRes:
                maxRes = result

            if result >= _WORD_PRESENCE_TRESHOLDER and i <= endIndex:
                # rating += result
                endIndex = endSlice
                # count += 1
            elif i > endIndex:
                if startIndex != endIndex:
                    listTimeInterval.append((startIndex * coefIndexToSec, endIndex * coefIndexToSec))
                    # listTimeInterval.append((startIndex, endIndex))
                                    
                if result >= _WORD_PRESENCE_TRESHOLDER:
                    # print(f'here {i}, {endSlice}')
                    startIndex, endIndex = i, endSlice
                else:
                    startIndex, endIndex = i, i
                # rating, count = 0.0, 0
                    
    # КОНЕЦ РАСКОММЕНТИТЬ


            # print(f'i = {int(i*coefIndexToSec*1000)}, end = {int(endSlice*coefIndexToSec*1000)}, match = {result}')

            if abs(_WORD_PRESENCE_TRESHOLDER - result) < 0.1:
                i += 2
            else:
                i += ceil(_STANDART_STEP * sizeReference)
        # РАСКОММЕНТИТЬ

        if startIndex != endIndex:
            # listTimeInterval.append((startIndex, endIndex))
            listTimeInterval.append((startIndex * coefIndexToSec, endIndex * coefIndexToSec))
            

        # здесь мы возвращаем сейчас время в секундах
        # print(f'index: {index}, indexEnd: {index + sizeReference}')
        # print(len(userFrames))
        print('--'*15)
        # print(maxRes)
        return listTimeInterval


    def getExactLocationWord(self, listWordBounds, referenceFrames, userFrames, coefficientIndexToSec):
        """
        Функция ищет точное место запретного слова
        На вход: список tuple (начало слова, конец слова) в миллисекундах; референсное MFCC; коээфициент, которым перевели индексы в секунды
        На выход: тайминг слова
        """
        listTimeInterval = []
        coefficientTimeToMfccIndex = 1000 * coefficientIndexToSec
        # print('last find')
        maxMatch, timeMatch = 0.0, (0, 0)
        for time in listWordBounds:
            # print(f'frames: {int(time[0] / coefficientTimeToMfccIndex)}: {ceil(time[1] / coefficientTimeToMfccIndex)} ')
            _ = self.crossValidation(referenceFrames, userFrames[int(time[0] / coefficientTimeToMfccIndex): ceil(time[1] / coefficientTimeToMfccIndex)])
            print(_, time)
            if _ >= _WORD_PRESENCE_TRESHOLDER:
                listTimeInterval.append((time[0], time[1], _))
            elif _ > maxMatch:
                    maxMatch = _
                    timeMatch = time
        if listTimeInterval:
            return listTimeInterval
        else:
            return [(timeMatch[0], timeMatch[1], maxMatch)]
        

# if __name__=='__main__':

    
#     # mfccRef = MFCC('/home/dasha/python_diplom/ASR/wavs/training/in_db_sd_low_spl/five-5-0-m.wav')
#     mfccRef = MFCC('/home/dasha/python_diplom/reference/imba.wav')
#     # mfccRef = MFCC('/home/dasha/python_diplom/cut_res/five-in-sentence-cut.wav')
#     mfccRef.calculateMFCC()
#     compare = Compare()

    # for file in ['/home/dasha/python_diplom/ASR/wavs/training/in_db_sd_low_spl/two-2-0-m.wav', '/home/dasha/python_diplom/ASR/wavs/training/in_db_sd_low_spl/seven-7-0-m.wav', '/home/dasha/python_diplom/ASR/wavs/training/in_db_sd_low_spl/one-1-5-m.wav', '/home/dasha/python_diplom/ASR/wavs/training/in_db_sd_low_spl/five-5-5-m.wav']:
    # for file in ['/home/dasha/python_diplom/wav/hello-dasha.wav', '/home/dasha/python_diplom/wav/five-in-sentence.wav', '/home/dasha/python_diplom/wav/one-five.wav', '/home/dasha/python_diplom/wav/no-five.wav',  '/home/dasha/python_diplom/ASR/wavs/training/in_db_sd_low_spl/five-5-0-m.wav', '/home/dasha/python_diplom/ASR/wavs/training/in_db_sd_low_spl/five-5-5-m.wav']:
    # print(os.listdir(directoryWithAudio))
    # for file in os.listdir(directoryWithAudio):
    #     mfcc1 = MFCC(directoryWithAudio + file)
    #     print(file.split('/')[-1])
    #     mfcc1.calculateMFCC()
    #     # compare.crossValidation(mfccRef.listFrames, mfcc1.listFrames)
    #     print(compare.crossValidationLongAudio(mfccRef.listFrames, mfcc1.listFrames, mfcc1.lengthMs, mfcc1.shiftMs))
    #     print('-'*15)
    #     break

