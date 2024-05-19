from multiprocessing import Process, Pool


# def print_func(continent='Asia'):
#     print('The name of continent is : ', continent)

# if __name__ == "__main__":  # confirms that the code is under main function
#     names = ['America', 'Europe', 'Africa']
#     procs = []
#     proc = Process(target=print_func)  # instantiating without any argument
#     procs.append(proc)
#     proc.start()

#     # instantiating process with arguments
#     for name in names:
#         # print(name)
#         proc = Process(target=print_func, args=(name,))
#         procs.append(proc)
#         proc.start()

#     # complete the processes
#     for proc in procs:
#         proc.join()


# import time

# work = (["A", 5], ["B", 2], ["C", 1], ["D", 3])


# def work_log(work_data):
#     print(" Process %s waiting %s seconds" % (work_data[0], work_data[1]))
#     time.sleep(int(work_data[1]))
#     print(" Process %s Finished." % work_data[0])


# def pool_handler():
#     p = Pool(2)
#     p.map(work_log, work)


# if __name__ == '__main__':
#     pool_handler()


from segmentationAudio import *
from databases import *

directoryWithAudio = '/home/dasha/python_diplom/wav/'

def bla(listArgument):

    listTimes = compare.crossValidationLongAudio(referenceFrames=listArgument[1], userFrames=listArgument[2], coefIndexToSec=listArgument[3])
    temporary = []
    for time in listTimes:
        temporary.extend(segmentation.searchWordsInAudioFragment(start=time[0], finish=time[1]))
    listTimes = compare.getExactLocationWord(temporary, listArgument[1], listArgument[2], listArgument[3])
    return (listArgument[0], listTimes)
        

    # return (listArgument[0], compare.crossValidationLongAudio(referenceFrames=listArgument[1], userFrames=listArgument[2], coefIndexToSec=listArgument[3]))



if __name__=='__main__':

    audio = Audio(directoryWithAudio + 'user_v.1.wav')
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
    # for name, frames in dictionaryReference.items():

    #     print('\n' + name)
    #     dictWordAndTime[name] = compare.crossValidationLongAudio(referenceFrames=frames, userFrames=mfcc.listFrames, coefIndexToSec=mfcc.lengthMs-mfcc.shiftMs)
    # print(dictWordAndTime)

    # print('*'*15)

    listToProcess = []
    for name, frames in dictionaryReference.items():
        listToProcess.append((name, frames, mfcc.listFrames, mfcc.lengthMs-mfcc.shiftMs))

    with Pool() as p:
        results = p.map(bla, listToProcess)

    tempDict = dict()
    for result in results:
        # dictWordAndTime[result[0]] = result[1]
        for time in result[1]:
            start, end, score = int(time[0]), int(time[1]), time[2]

            if (start, end) in tempDict:
                if tempDict[(start, end)][0] < score:
                    tempDict[(start, end)] = (score, result[0])
            else:
                tempDict[(start, end)] = (score, result[0])


    # print(dictWordAndTime)

    # for name, listTimes in dictWordAndTime.items():
    #     for time in listTimes:

    #         start, end, score = int(time[0]), int(time[1]), time[2]

    #         if (start, end) in tempDict:
    #             if tempDict[(start, end)][0] < score:
    #                 tempDict[(start, end)] = (score, name)
    #         else:
    #             tempDict[(start, end)] = (score, name)

    dictWordAndTime.clear()

    for key, value in tempDict.items():
        if value[1] not in dictWordAndTime:
            dictWordAndTime[value[1]] = []
        
        dictWordAndTime[value[1]].append((key[0], key[1], value[0]))

    for name, listTimes in dictWordAndTime.items():
        for time in listTimes:
            trimmed_audio = audio.audioData[int(time[0]):ceil(time[1])]
            trimmed_audio.export(f"/home/dasha/python_diplom/cut_res/{name}-{int(time[0])}:{int(time[1])}.wav", format="wav")


    print(f'-------------------------------\nlaaast: {dictWordAndTime}')