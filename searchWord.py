from segmentationAudio import *
from databases import *
from generateWord import *

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
    onlyFileName = 'user_v.9'
    fileName = '/home/dasha/python_diplom/wav/user_v.9.wav'
    audio = Audio(fileName)
    # audio = Audio()

    mfcc = MFCC(audio=audio)
    segmentation = SegmentationWord(audio=audio)
    compare = Compare()
    generatorWord = GeneratorAudio(speaker=fileName)


    dictWordAndTime = {}

    db = Database()
    db.connect()
    dictionaryReference = db.getMFCCFromDB()
    dictionaryReplacement = db.getDictCategoryReplacement()
    db.disconnect()


    # загрузили аудио от юзера
    # audio.updateData('/home/dasha/python_diplom/wav/user_v.1.wav')
    mfcc.calculateMFCC()

    ############################

    # Test подбор размера окна для референса

    # dictWordAndWindows = {'medium': [], '1/4 * max': [], '1/3 * max': [], '1/2 * max': [], '2/3 * max': []}

    # for file in ['user_v.1.wav', 'user_v.2.wav', 'user_v.3.wav', 'user_v.9.wav', 'user_v.10.wav']:
    #     audio.updateData(directoryWithAudio + file)
    #     mfcc.calculateMFCC()
    #     for name, frames in dictionaryReference.items():
    #         print('-'*30)
    #         print(name)
    #         temp = compare.testForSizeWindow(referenceFrames=frames, userFrames=mfcc.listFrames, coefIndexToSec=mfcc.lengthMs-mfcc.shiftMs)
    #         for i, res in enumerate(temp):
    #             if i == 0:
    #                 dictWordAndWindows['medium'].append(res)
    #             elif i == 1:
    #                 dictWordAndWindows['1/4 * max'].append(res)
    #             elif i == 2:
    #                 dictWordAndWindows['1/3 * max'].append(res)
    #             elif i == 3:
    #                 dictWordAndWindows['1/2 * max'].append(res)
    #             elif i == 4:
    #                 dictWordAndWindows['2/3 * max'].append(res)
    
    # for key, value in dictWordAndWindows.items():
    #     print(f'{key} : {np.std(value)}')

    # Конец теста



    ############################
    # Test подбор порога


    # listMaxWeight = []
    # for name, frames in dictionaryReference.items():
    #     print(name)

    #     if name == 'imba':
    #         # print(name)
    #         for fr in frames:
    #             listMaxWeight.append(fr[1])
    #         break
    
    # print(listMaxWeight)
    # dictRange = dict()

    # prev = 0.15
    # for maxWeight in listMaxWeight:
    #     temp = []
    #     i = prev
    #     while i < maxWeight:
    #         temp.append(i)
    #         i = round(i + 0.1, 2)
    #     prev = maxWeight
    #     dictRange[maxWeight] = temp


    # # keys = dictRange.keys()
    # weight_combinations = list(itertools.product(*[dictRange[key] for key in dictRange.keys()]))
    # print(weight_combinations)
    # mfcc.calculateMFCC()

    # for name, frames in dictionaryReference.items():
    #     for combiantion in weight_combinations:
    #         print(f'\nCombination {combiantion}')
    #         listFramesAndCombination = []
    #         for i, fr in enumerate(frames):
    #             listMFCCRef = fr[0]
    #             listFramesAndCombination.append((listMFCCRef, combiantion[i]))
    #         compare.crossValidationLongAudio(referenceFrames=listFramesAndCombination, userFrames=mfcc.listFrames, coefIndexToSec=mfcc.lengthMs-mfcc.shiftMs)
    #         print('***'*15)
    #         # break

            
    
    # print(weight_combinations)

    # The end test



    # sys.exit()
    # # посчитали для каждого референса, где че нашли
    for name, frames in dictionaryReference.items():

        print('\n' + name)
        dictWordAndTime[name] = compare._crossValidationLongAudio(referenceFrames=frames, userFrames=mfcc.listFrames, coefIndexToSec=mfcc.lengthMs-mfcc.shiftMs)
        # break
    print(dictWordAndTime)

    print('*'*15)

    # sys.exit()
    # теперь разделяем на сегменты части
    for name, listTimes in dictWordAndTime.items():
        temporary = []
        # print(name)
        for time in listTimes:
            bla = segmentation.searchWordsInAudioFragment(start=time[0], finish=time[1])
            temporary.extend(bla)
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
        dictWordAndTime[name] = compare._getExactLocationWord(listTimes, dictionaryReference[name], mfcc.listFrames, mfcc.lengthMs - mfcc.shiftMs)
        

    tempDict = dict()
    for name, listTimes in dictWordAndTime.items():
        for time in listTimes:

            start, end, score = time[0], time[1], time[2]

            if (start, end) in tempDict:
                if tempDict[(start, end)][0] < score:
                    tempDict[(start, end)] = (score, name)
            else:
                tempDict[(start, end)] = (score, name)

    dictWordAndTime.clear()

    tempDict = sorted(tempDict.items())
    print('Temp dict')
    print(tempDict)
    print('---'*15)


    print(tempDict)
    print('-'*12)

    if len(tempDict) > 1:
        i = 1
        while i < len(tempDict):
            if tempDict[i][0][0] < tempDict[i - 1][0][1]:
                if tempDict[i][1][0] > tempDict[i - 1][1][0]:
                    del tempDict[i - 1]
                else:
                    del tempDict[i]
            else:
                i += 1
    print(tempDict)

    # for key, value in tempDict.items():
    #     if value[1] not in dictWordAndTime:
    #         dictWordAndTime[value[1]] = []
        
    #     dictWordAndTime[value[1]].append((key[0], key[1], value[0]))


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
            


    # Раскоменть        
    # for name, listTimes in dictWordAndTime.items():
    #     for time in listTimes:
    #         trimmed_audio = audio.audioData[int(time[0]):ceil(time[1])]
    #         trimmed_audio.export(f"/home/dasha/python_diplom/cut_res/{name}-{int(time[0])}:{int(time[1])}.wav", format="wav")


    # print(f'-------------------------------\nlaaast: {dictWordAndTime}')

    begin = 0
    for time, meta in tempDict:
        name = meta[1]
        if isinstance(dictionaryReplacement[name], str):
            dictionaryReplacement[name] = generatorWord.generateWord(text=dictionaryReplacement[name])
        s = audio.audioData[begin:time[0]]
        if begin == 0:
            newAudio = s
        else:
            newAudio += s
        newAudio += dictionaryReplacement[name]

        # value for next loop
        begin = time[1]
    newAudio += audio.audioData[begin:]
    # newAudio.append(audio.audioData[begin:])
    newAudio.export(f"/home/dasha/python_diplom/cut_res/{onlyFileName}_result.wav", format="wav")

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
