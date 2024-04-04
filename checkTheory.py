import re
import statistics
fileData = open('/home/dasha/python_diplom/cringe.log')

listDTWRating = {}
localDTW = []
combination = None

while True:
    line = fileData.readline()
    if line != '\n':
        line = line.rstrip()
    # считываем строку
    # прерываем цикл, если строка пустая
    if re.match(r'^i = \d+, end = \d+, match = [\d\.]+$', line):
        result = float( re.split(r'match = ', line)[1])
        localDTW.append(result)
    elif re.match(r'^\*+$', line):
        data = {'mean': 0.0, '1.1*mean': 0.0, '1.2*mean': 0.0, 'median': 0.0, '1.1*median': 0.0, '1.2*median': 0.0}
        data['mean'], data['median'] = statistics.mean(localDTW), statistics.median(localDTW)
        data['1.1*mean'], data['1.2*mean'], data['1.1*median'], data['1.2*median'] = data['mean'] * 1.1, data['mean'] * 1.2, data['median'] * 1.1, data['median'] * 1.2

        listDTWRating[combination] = data
        # listDTWRating.append(localDTW)
        localDTW = []
        combination = None
    elif not line:
        break
    elif re.match(r'^Combination \(.*?\)$', line):
        combination = re.split(r'n ', line)[1]
    
    # выводим строку
        
for bla, value in listDTWRating.items():
    print(bla, value)