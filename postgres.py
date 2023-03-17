# https://softwareengineering.stackexchange.com/questions/200522/how-to-deal-with-database-connections-in-a-python-library-module

import psycopg2


class postgres(object):
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = object.__new__(cls)
            cls._instance.connection = None

            try:
                postgres._instance.connect()
            except Exception as error:
                print('Error: connection not established {}'.format(error))
                postgres._instance = None
                postgres._instance.connection = None
            else:
                print('Postgres connected')
        return cls._instance

    def __init__(self):
        try:
            self.connection = self._instance.connection
        except:
            print('init error')

    def connect(self):
        try:
            print('connecting to Postgres')
            db_config = {
                'host': 'server.local',
                'port': 5432,
                'sslmode': 'disable',
                'user': 'username',
                'password': 'password',
                'dbname': 'sensordata'}
            postgres._instance.connection = psycopg2.connect(**db_config)
        except:
            print('DB connection error')
            pass

    def check(self):
        try:
            cursor = self.connection.cursor()
            cursor.execute('SELECT 1')
            cursor.close()
        except Exception as error:
            print('db error: {}'.format(error))
            self.connect()
            return False
        else:
            return True

    def conn(self):
        return postgres._instance.connection


    def __del__(self):
        try:
            self.connection.close()
        except:
            pass
        print('Postgres disconnected')
