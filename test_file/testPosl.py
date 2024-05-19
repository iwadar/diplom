# tempDict = {(75, 438): (2.28992478610051, 'cringe'), (6795, 7199): (2.265331310250912, 'cringe'), (4005, 4206): (2.1706204196758865, 'imba'), (6868, 7205): (2.2036787663788733, 'imba')}


# tempDict = {(1, 2): (2.2, 'cringe'), 
#             (1.5, 2.5): (2.4, 'imba'),
#             (2.23, 5): (2.4, 'skuf'),
#             (4, 4.5): (3.2, 'imba'),
#             (5, 6): (2.2, 'cringe'),
#             (6, 8): (2.3, 'cringe'),}
from audio import *
from generateWord import *

tempDict = [((614, 989), (2.1647726828123512, 'cringe')), ((3004, 3466), (2.2638302923980627, 'cringe')), ((3827, 4280), (2.086044470747393, 'imba'))]
# tempDict = sorted(tempDict.items())

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

# for start, end in tempDict:
#     print(start, end)

onlyFileName = 'user_v.2'
fileName = '/home/dasha/python_diplom/wav/user_v.2.wav'
generatorWord = GeneratorAudio(speaker=fileName)

audio = Audio(fileName)
dictionaryReplacement = {'cringe': 'стыд', 'imba': 'круто'}
begin = 0
for time, meta in tempDict:
    name = meta[1]
    if isinstance(dictionaryReplacement[name], str):
        dictionaryReplacement[name] = generatorWord.generateWord(text=dictionaryReplacement[name])
    s = audio.audioData[begin:time[0]]
    print(begin, time[0])
    if begin == 0:
        newAudio = s
    else:
        print('тут')
        newAudio += s
    newAudio += dictionaryReplacement[name]

    # value for next loop
    begin = time[1]

# newAudio.append(audio.audioData[begin:])
newAudio.export(f"/home/dasha/python_diplom/cut_res/{onlyFileName}_result.wav", format="wav")
