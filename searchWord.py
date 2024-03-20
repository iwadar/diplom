from mfcc import *
from segmentationAudio import *
import os


if __name__=='__main__':
    audio = Audio('/home/dasha/python_diplom/ASR/wavs/training/in_db_sd_low_spl/five-5-0-m.wav')
    mfccRef = MFCC(audio=audio)
    compare = Compare()

    mfccRef.calculateMFCC()

    # print(os.listdir(directoryWithAudio))
    # for file in os.listdir(directoryWithAudio):
    for file in ['/home/dasha/python_diplom/wav/one-five.wav']:

        # audio_input = Audio(directoryWithAudio + file)
        audio_input = Audio(file)
        mfcc1 = MFCC(audio_input)
        print(file.split('/')[-1])
        mfcc1.calculateMFCC()
        # compare.crossValidation(mfccRef.listFrames, mfcc1.listFrames)
        print(compare.crossValidationLongAudio(mfccRef.listFrames, mfcc1.listFrames, mfcc1.lengthMs, mfcc1.shiftMs))
        print('-'*15)
        print(compare.getExactLocationWord([(1391.3378684807255, 1511.9274376417234), (2037.0521541950113, 2094.6938775510203)], mfccRef.listFrames, mfcc1.listFrames, mfcc1.lengthMs-mfcc1.shiftMs))
        print('-'*15)
