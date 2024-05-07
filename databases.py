import configparser
import os.path
import pickle
import psycopg2
from mfcc import *
from audio import *
import re

_CONFIG_NAME = 'configDataBases.ini'
_LOCALHOST = 'localhost'
_DATABASE = 'Database'
_HOST = 'host'
_USER = 'user'
_DBNAME = 'dbname'
_PASSWORD = 'password'
_NOT_EXIST = -1

directoryWithReference = '/home/dasha/python_diplom/reference/' 


class Config:
    def __init__(self) -> None:
        self.config = configparser.ConfigParser()
        if not os.path.exists(_CONFIG_NAME):
            self.config.add_section(_DATABASE)

            self.config.set(_DATABASE, _HOST, (input('Host (Press Enter, if host is localhost): ') or _LOCALHOST))
            self.config.set(_DATABASE, _DBNAME, input('Database name: '))
            self.config.set(_DATABASE, _USER, input('Login: '))
            self.config.set(_DATABASE, _PASSWORD, input('Password: '))
        else:
            self.config.read(_CONFIG_NAME)
            if self.config[_DATABASE][_USER] == '':
                self.config.set(_DATABASE, _USER, input('User: '))

            if self.config[_DATABASE][_PASSWORD] == '':
                self.config.set(_DATABASE, _PASSWORD, input('Password: '))
            
            if self.config[_DATABASE][_HOST] == '':
                self.config.set(_DATABASE, _HOST, (input('Host (Press Enter, if host is localhost): ') or _LOCALHOST))

            if self.config[_DATABASE][_DBNAME] == '':
                self.config.set(_DATABASE, _DBNAME, input('Database name: '))

        with open(_CONFIG_NAME, "w") as config_file:
            self.config.write(config_file)


class Database:
    def __init__(self) -> None:
        self.config = Config()

    def connect(self):
        try:
            self.connection = psycopg2.connect(dbname=self.config.config[_DATABASE][_DBNAME],
                                                user=self.config.config[_DATABASE][_USER],
                                                password=self.config.config[_DATABASE][_PASSWORD],
                                                host=self.config.config[_DATABASE][_HOST])
            
            print('Database connection established successfully')
            self.cursor = self.connection.cursor()
        except:
            print('Can\'t establish connection to database')

    def disconnect(self):
        try:
            self.connection.close()
            print('Database disconnected')
        except:
            print('Disconnect failed!')


    def insertToReferenceWord(self, tableName, categoryId, mfcc, weight):
        try:
            self.cursor.execute(f"INSERT INTO {tableName} (categoryid, mfcc, weight) VALUES  (%s, %s, %s)", (categoryId, mfcc, weight))
            self.connection.commit()
            print('Entry added successfully!')
        except Exception as e:
            print(f'Adding completed with error: {e}')


    def getMFCCFromDB(self, categoryreplacement = 'categoryreplacement', referenceword='referenceword'):
        self.cursor.execute(f"""SELECT {categoryreplacement}.word, {referenceword}.mfcc, {referenceword}.weight FROM {categoryreplacement}, {referenceword}
                                WHERE {referenceword}.categoryid = {categoryreplacement}.id
                                ORDER BY {categoryreplacement}.word, {referenceword}.weight""")

        rows = self.cursor.fetchall()
        dictNameAndMfcc = dict()

        # 0 - id category, 1 - mfcc, 2 - weight
        for each in rows:
            # print(each)
            if each[0] not in dictNameAndMfcc:
                dictNameAndMfcc[each[0]] = []
            # dictNameAndMfcc[each[0]].append(pickle.loads(each[1]))
            dictNameAndMfcc[each[0]].append((pickle.loads(each[1]), each[2]))

        # print(dictNameAndMfcc)
        return dictNameAndMfcc


    def getDictCategoryReplacement(self, categoryreplacement = 'categoryreplacement'):
        self.cursor.execute(f"""SELECT {categoryreplacement}.word, {categoryreplacement}.replacement FROM {categoryreplacement}""")

        rows = self.cursor.fetchall()
        dictNameAndReplacement = dict()

        # 0 - word, 1 - replacement
        for each in rows:
            dictNameAndReplacement[each[0]] = each[1]

        return dictNameAndReplacement



    def isExistWord(self, tableName, word):

        self.cursor.execute(f"SELECT id FROM {tableName} WHERE word='{word}'")
        rows = self.cursor.fetchall()
        if rows:
            return rows[0][0]
        else:
            return _NOT_EXIST
    
    
    def insertToCategoryReplacment(self, tableName, word, replacement = ''):
        try:
            self.cursor.execute(f"INSERT INTO {tableName} (word, replacement) VALUES ('{word}', '{replacement}') RETURNING id")
            insertedID = self.cursor.fetchone()[0]
            self.connection.commit()
            # print('Entry added successfully!')
            return insertedID
        except Exception as e:
            print(f'Adding completed with error: {e}')


    def insertNewReferenceToDb(self, filename, mfcc):
        word_weight = re.split("_| ", os.path.splitext(filename)[0])
        if len(word_weight) < 2:
            print('Bad filename! (category_weight.wav)')
            return
        word, weight = word_weight[0], float(word_weight[1])

        # 
        # if word != 'imba':
        #     return
        # 

        if weight > 1.0 or weight < 0.0:
            print('Bad weight! [0, 1]')
            return
        
        mfccToDb = pickle.dumps(mfcc)

        # Если такого слова еще нет, то надо добавить его в categoryreplacment
        if (idWord := self.isExistWord(tableName='categoryreplacement', word=word)) == _NOT_EXIST:
            idWord = self.insertToCategoryReplacment(tableName='categoryreplacement', word=word)
        
        self.insertToReferenceWord(tableName='referenceword', categoryId=idWord, mfcc=mfccToDb, weight=weight)



if __name__=='__main__':
    db = Database()
    db.connect()

    audio = Audio()
    mfcc = MFCC(audio=audio)
    # file = 'imba_0.59.wav'

    for file in os.listdir(directoryWithReference):
        if os.path.isfile(directoryWithReference + file):
            print(directoryWithReference + file)
            audio.updateData(directoryWithReference + file)
            mfcc.calculateMFCC()
            mfcc.listFrames = stats.zscore(mfcc.listFrames)
            db.insertNewReferenceToDb(file, mfcc.listFrames)
    db.disconnect()
    
#     #     ## Create a semi-complex list to pickle
#     # listToPickle = [(10, 10), (20, 10.0), (1.0, 2.0)]

#     # ## Pickle the list into a string
#     # pickledList = pickle.dumps(listToPickle)

#     # # db.insertInformationToDB(tableName='test2', name='cring_1', mfcc=pickledList)
#     # db.selectMFCCFromDB(tableName='test2')
    # db.getMFCCFromDB()

    

