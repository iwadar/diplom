import librosa
import numpy as np


def readFile(fileName: str):
    data, sampleRate = librosa.load(fileName)
    return data, sampleRate


def preEmphasis(data):
    data = librosa.effects.preemphasis(data)
    return data
    

def framing(data, sampleRate, length=0.025, shift=0.010):
    length = int(round(sampleRate * length))
    shift = int(round(sampleRate * shift))

    print(f'Length = {length}, shift={shift}')

    frames = list()

    for i in range(0, len(data), length - shift): # я считаю сдвиг должен быть length - shift
    
    # for i in range(0, len(data), shift): # я считаю сдвиг должен быть length - shift
        frame = data[i:i+length] # делаем срез

        if len(frame) != length: # если не хватает попали на конец данных, забили нулями
            frame = np.pad(frame, (0, (length-len(frame))), mode='constant')

        frames.append(frame)

    return length, np.array(frames)




if __name__=='__main__':

    data, sampleRate = readFile('/home/dasha/python_diplom/ASR/wavs/training/in_db_sd_low_spl/five-5-0-m.wav')
    data = preEmphasis(data)

    length, data = framing(data=data, sampleRate=sampleRate)
    print(data)
