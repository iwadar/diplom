from multiprocessing import Pool
from segmentationAudio import *
from databases import *
from generateWord import *
from pathlib import Path
import gc


class ParallelFind:
    # pathToDownload = str(Path.home() / "Downloads/TalkSlang")
    pathToDownload = '/home/dasha/python_diplom/cut_res/'
    os.makedirs(pathToDownload, mode=0o777, exist_ok=True)

    def __init__(self, fileName) -> None:
        # создали объекты
        self.fileName = fileName
        self.compare = Compare()
        self.audio = Audio(fileName)
        self.mfcc = MFCC(audio=self.audio)
        self.segmentation = SegmentationWord(audio=self.audio)
        # self.generatorWord = GeneratorAudio(speaker=self.fileName)
        db = Database()
        self.dictWordAndTime = {}
        self.average_dBFS_original = self.audio.audioData.dBFS
        print(self.average_dBFS_original)

        # проинициализаировали
        db.connect()
        self.dictionaryReference = db.getMFCCFromDB()
        self.dictionaryReplacement = db.getDictCategoryReplacement()
        db.disconnect()
        self.mfcc.calculateMFCC()
        # print(self.mfcc.listFrames)


    def parallelFunction(self, listArguments):
        # 0 - name, 1 - reference frames, 2 - cur frames, 3 - numbers
        listTimes = self.compare._crossValidationLongAudio(referenceFrames=listArguments[1], userFrames=listArguments[2], coefIndexToSec=listArguments[3])
        temporary = []
        for time in listTimes:
            temporary.extend(self.segmentation.searchWordsInAudioFragment(start=time[0], finish=time[1]))
        listTimes = self.compare._getExactLocationWord(temporary, listArguments[1], listArguments[2], listArguments[3])
        print(listArguments[0], listTimes)
        # if listTimes:
        #     self.dictionaryReplacement[listArguments[0]] = self.generatorWord.generateWord(text=self.dictionaryReplacement[listArguments[0]])
        #     average_dBFS_new = abs(self.dictionaryReplacement[listArguments[0]].dBFS)
        #     self.dictionaryReplacement[listArguments[0]] = self.dictionaryReplacement[listArguments[0]].apply_gain(self.average_dBFS_original - average_dBFS_new)
        return (listArguments[0], listTimes)


    def findAndReplaceWords(self):

        listToProcess = []
        for name, frames in self.dictionaryReference.items():
            listToProcess.append((name, frames, self.mfcc.listFrames, self.mfcc.lengthMs-self.mfcc.shiftMs))

        with Pool() as p:
            results = p.map(self.parallelFunction, listToProcess)

        tempDict = dict()
        for result in results:
            for time in result[1]:

                start, end, score = time[0], time[1], time[2]
                if (start, end) in tempDict:
                    if tempDict[(start, end)][0] < score:
                        tempDict[(start, end)] = (score, result[0])
                else:
                    tempDict[(start, end)] = (score, result[0])
        
        tempDict = sorted(tempDict.items())

        if len(tempDict) > 1 and tempDict[0][0][0] < 200:
            del tempDict[0]

        if len(tempDict) > 1:
            i = 1
            while i < len(tempDict):
                print(tempDict[i][0][0])
                if tempDict[i][0][0] < tempDict[i - 1][0][1]:
                    if tempDict[i][1][0] > tempDict[i - 1][1][0]:
                        del tempDict[i - 1]
                    else:
                        del tempDict[i]
                else:
                    i += 1

        # tempDict = [((4506.632653061225, 5037.063492063493), (2.239908195731812, 'cringe')), ((9452.857142857143, 9965.374149659863), (2.151802037668552, 'cringe'))]

        print('-'*12)
        print(len(tempDict))
        print(tempDict)
        if len(tempDict):
            begin = 0
            self.generatorWord = GeneratorAudio(speaker=self.fileName)
            newAudio = AudioSegment.silent()
            for time, meta in tempDict:
                name = meta[1]
                if isinstance(self.dictionaryReplacement[name], str):
                    self.dictionaryReplacement[name] = self.generatorWord.generateWord(text=self.dictionaryReplacement[name])
                    print(self.dictionaryReplacement[name].dBFS)
                    average_dBFS_new = self.dictionaryReplacement[name].dBFS
                    print(f"разность = {(self.average_dBFS_original - average_dBFS_new)}")
                    self.dictionaryReplacement[name] = self.dictionaryReplacement[name] + (self.average_dBFS_original - average_dBFS_new)
                    print(self.dictionaryReplacement[name].dBFS)
                s = self.audio.audioData[begin:time[0]]
                if begin == 0:
                    newAudio = s
                else:
                    newAudio += s

                newAudio += self.dictionaryReplacement[name]

                begin = time[1]
            del self.generatorWord.tts
            del self.generatorWord
            gc.collect()
            newAudio += self.audio.audioData[begin:]
            newAudio.export(self.pathToDownload + f"{Path(self.fileName).stem}_result.wav", format="wav")
            print(f'Result in file {self.pathToDownload + f"{Path(self.fileName).stem}_result.wav"}')
            return self.pathToDownload + f"{Path(self.fileName).stem}_result.wav"
        else:
            print('В файле не обнаружено слов зарегистрированных слов.')
            return 'В файле не обнаружено слов зарегистрированных слов.'



if __name__=='__main__':
    # for i in ['1', '2', '3', '8', '9']:
    #     print(i)
    #     proga = ParallelFind(f'/home/dasha/python_diplom/wav/user_v.{i}.wav')
    #     proga.findAndReplaceWords()
    #     del proga

    proga = ParallelFind(f'/home/dasha/python_diplom/wav/cringe_1.wav')
    proga.findAndReplaceWords()
