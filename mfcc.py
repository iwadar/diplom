import librosa
import numpy as np
from fastdtw import fastdtw

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

        for userFrame in userFrames:
            dmin, jmin = np.inf, -1
            for j, referenceFrame in enumerate(referenceFrames):
                res, _ = fastdtw(userFrame, referenceFrame, dist=lambda userFrame, referenceFrame: np.linalg.norm(userFrame - referenceFrame, ord=1))
                if res < dmin:
                    dmin = res
                    jmin = j

        print(dmin, jmin)


if __name__=='__main__':

    mfccRef = MFCC('/home/dasha/python_diplom/ASR/wavs/training/in_db_sd_low_spl/five-5-0-m.wav')
    mfccRef.calculateMFCC()

    mfcc1 = MFCC('/home/dasha/python_diplom/ASR/wavs/training/in_db_sd_low_spl/five-5-1-m.wav')
    mfcc1.calculateMFCC()

    Compare().crossValidation(mfccRef.listFrames, mfcc1.listFrames)

