from segmentationAudio import *
import os, sys
import copy
from databases import *

directoryWithAudio = '/home/dasha/python_diplom/wav/'
directoryWithReference = '/home/dasha/python_diplom/reference/' 



def connectWordTime(listWordTimeBorders):
        if len(listWordTimeBorders) == 1:
            return listWordTimeBorders
        newWordTimeBorder = []
        i = 1
        while i < len(listWordTimeBorders) + 1:
            start = listWordTimeBorders[i - 1][0]
            finish = listWordTimeBorders[i - 1][1]
            if i != len(listWordTimeBorders):
                while listWordTimeBorders[i][0] - listWordTimeBorders[i - 1][1] <= 75.0:
                    finish = listWordTimeBorders[i][1]
                    i += 1
                    if i >= len(listWordTimeBorders):
                        break
            if finish - start > 100.0:
                newWordTimeBorder.append((start, finish))
            i += 1
            

        # for i in range(1, len(listWordTimeBorders) - 1):
        #     if listWordTimeBorders[i][0] - listWordTimeBorders[i - 1][1] <= self._thresholdWordSample:
        #         newWordTimeBorder.append(listWordTimeBorders[i - 1][0], listWordTimeBorders[i][1])
        #     else:
        #         newWordTimeBorder.append
        return newWordTimeBorder


if __name__=='__main__':

    audio = Audio('/home/dasha/python_diplom/wav/user_v.9.wav')
    mfcc = MFCC(audio=audio)
    segmentation = SegmentationWord(audio=audio)
    compare = Compare()


    dictWordAndTime = {}

    db = Database()
    db.connect()
    dictionaryReference = db.getMFCCFromDB()
    db.disconnect()


    # загрузили аудио от юзера
    # audio.updateData('/home/dasha/python_diplom/wav/user_v.1.wav')
    mfcc.calculateMFCC()

    # посчитали для каждого референса, где че нашли
    for name, frames in dictionaryReference.items():

        print('\n' + name)
        dictWordAndTime[name] = compare.crossValidationLongAudio(referenceFrames=frames, userFrames=mfcc.listFrames, coefIndexToSec=mfcc.lengthMs-mfcc.shiftMs)
    print(dictWordAndTime)

    print('*'*15)

    # sys.exit()
    # dictWordAndTime['imba'] = [(0.915, 6.945, 0.8250500038823403)]
    # теперь разделяем на сегменты части
    for name, listTimes in dictWordAndTime.items():
        temporary = []
        # print(name)
        for time in listTimes:
            temporary.extend(segmentation.searchWordsInAudioFragment(start=time[0], finish=time[1]))
        # print(f'{name}: {temporary}')
        dictWordAndTime[name] = temporary
            
        # dictWordAndTime[name] = connectWordTime(temporary)
        # print(f'{name}: {dictWordAndTime[name]}')
        # print('-'*15)


    print('-'*15 + f'\nSegment\n {dictWordAndTime}\n')

    print('**'*12)

    
    # sys.exit()
    for name, listTimes in dictWordAndTime.items():
        print(f'-------------------------------\n{name}')
        dictWordAndTime[name] = compare.getExactLocationWord(listTimes, dictionaryReference[name], mfcc.listFrames, mfcc.lengthMs - mfcc.shiftMs)
        

    tempDict = dict()
    for name, listTimes in dictWordAndTime.items():
        for time in listTimes:

            start, end, score = int(time[0]), int(time[1]), time[2]

            if (start, end) in tempDict:
                if tempDict[(start, end)][0] < score:
                    tempDict[(start, end)] = (score, name)
            else:
                tempDict[(start, end)] = (score, name)

    dictWordAndTime.clear()

    for key, value in tempDict.items():
        if value[1] not in dictWordAndTime:
            dictWordAndTime[value[1]] = []
        
        dictWordAndTime[value[1]].append((key[0], key[1], value[0]))


        # seen_times = set()
        # to_remove = []
        # for i, tpl in enumerate(dictWordAndTime[key]):
        #     start, end, score = tpl
        #     if start in seen_times or end in seen_times:
        #         to_remove.append(i)
        #     else:
        #         seen_times.add(start)
        #         seen_times.add(end)
        # for i in reversed(to_remove):
        #     del dictWordAndTime[key][i]
            
    for name, listTimes in dictWordAndTime.items():
        for time in listTimes:
            trimmed_audio = audio.audioData[int(time[0]):ceil(time[1])]
            trimmed_audio.export(f"/home/dasha/python_diplom/cut_res/{name}-{int(time[0])}:{int(time[1])}.wav", format="wav")


    print(f'-------------------------------\nlaaast: {dictWordAndTime}')

    # print(dictionaryReference)

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
