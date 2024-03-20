from mfcc import *
from segmentationAudio import *
import os, sys
import copy

directoryWithAudio = '/home/dasha/python_diplom/wav/'
directoryWithReference = '/home/dasha/python_diplom/reference/' 



if __name__=='__main__':

    # audio = Audio('/home/dasha/python_diplom/reference/imba.wav')
    # mfcc = MFCC(audio=audio)
    # mfcc.calculateMFCC()
    # compare = Compare()

    audio = Audio()
    mfcc = MFCC(audio=audio)
    segmentation = SegmentationWord(audio=audio)

    compare = Compare()


    dictionaryReference = dict()

    dictWordAndTime = {}

    #загрузили референсы
    for file in os.listdir(directoryWithReference):
        audio.updateData(directoryWithReference + file)
        mfcc.calculateMFCC()
        dictionaryReference[os.path.splitext(file)[0]] = copy.deepcopy(mfcc.listFrames)
        dictWordAndTime[os.path.splitext(file)[0]] = []
    
    if (dictionaryReference['imba'] == dictionaryReference['cringe_1']).all():
        print (f'imba: {dictionaryReference["imba"]}\ncringe: {dictionaryReference["cringe_1"]}')
    # загрузили аудио от юзера
    audio.updateData('/home/dasha/python_diplom/wav/user_v.1.wav')
    mfcc.calculateMFCC()

    # посчитали для каждого референса, где че нашли
    for name, frames in dictionaryReference.items():
        print(name)
        dictWordAndTime[name].extend(compare.crossValidationLongAudio(referenceFrames=frames, userFrames=mfcc.listFrames, length=mfcc.lengthMs, shift=mfcc.shiftMs))
    #     break
    # print(dictWordAndTime)

    # sys.exit()
    # теперь разделяем на сегменты части
    for name, listTimes in dictWordAndTime.items():
        temporary = []
        for time in listTimes:
            temporary.extend(segmentation.searchWordsInAudioFragment(start=time[0], finish=time[1]))
        dictWordAndTime[name] = temporary

    print(dictWordAndTime)
    

    for name, listTimes in dictWordAndTime.items():
        dictWordAndTime[name] = compare.getExactLocationWord(listTimes, dictionaryReference[name], mfcc.listFrames, mfcc.lengthMs - mfcc.shiftMs)
        

        for time in dictWordAndTime[name]:
                trimmed_audio = audio.audioData[int(time[0]):ceil(time[1])]
                trimmed_audio.export(f"/home/dasha/python_diplom/cut_res/{name}-{time[0]}:{time[1]}.wav", format="wav")

    print(f'laaast: {dictWordAndTime}')



    # print(os.listdir(directoryWithAudio))
    # for file in os.listdir(directoryWithAudio):
    # for file in ['/home/dasha/python_diplom/wav/many-five.wav']:

        # audio_input = Audio(directoryWithAudio + file)
        # audio_input = Audio(file)
        # mfcc1 = MFCC(audio_input)
        # print(file.split('/')[-1])
        # mfcc1.calculateMFCC()
        # # compare.crossValidation(mfccRef.listFrames, mfcc1.listFrames)
        # # print(compare.crossValidationLongAudio(mfccRef.listFrames, mfcc1.listFrames, mfcc1.lengthMs, mfcc1.shiftMs))
        # # print('-'*15)
        # print(compare.getExactLocationWord([(2379.5691609977325, 2506.190476190476), (2507.9138321995465, 2744.467120181406), (3173.5827664399094, 3284.013605442177), (3295.4875283446713, 3496.485260770975)], mfccRef.listFrames, mfcc1.listFrames, mfcc1.lengthMs-mfcc1.shiftMs))
        # print('-'*15)
