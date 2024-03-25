import configparser
import os.path
import pickle
import psycopg2
_CONFIG_NAME = 'configDataBases.ini'
_LOCALHOST = 'localhost'
_DATABASE = 'Database'
_HOST = 'host'
_USER = 'user'
_DBNAME = 'dbname'
_PASSWORD = 'password'


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
        except:
            print('Disconnect failed!')

    def insertInformationToDB(self, tableName, name, mfcc):
        try:
            self.cursor.execute(f"INSERT INTO {tableName} (name, mfcc) VALUES (%s, %s)", (name, mfcc))
            self.connection.commit()
            print('Entry added successfully!')
        except Exception as e:
            print(f'Adding completed with error: {e}')

    def selectMFCCFromDB(self, tableName):
        self.cursor.execute(f'SELECT * FROM {tableName}')

        rows = self.cursor.fetchall()
        dictNameAndMfcc = dict()
        ## Get the results
        for each in rows:
            # print(each)
            dictNameAndMfcc[each[1]] = pickle.loads(each[2])
        
        print(dictNameAndMfcc)
        return dictNameAndMfcc
            ## The result is also in a tuple
                
                ## Unpickle the stored string
                # unpickledList = pickle.loads(pickledStoredList)
                # print(unpickledList)



if __name__=='__main__':
    db = Database()
    db.connect()


        ## Create a semi-complex list to pickle
    listToPickle = [(10, 10), (20, 10.0), (1.0, 2.0)]

    ## Pickle the list into a string
    pickledList = pickle.dumps(listToPickle)

    # db.insertInformationToDB(tableName='test2', name='cring_1', mfcc=pickledList)
    db.selectMFCCFromDB(tableName='test2')

    db.disconnect()
    
