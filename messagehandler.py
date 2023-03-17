from regexmatcher import regexmatcher
from datetime import datetime
from psycopg2 import sql

def boolString2Int(string):
    try:
        retValue = ['false', 'true'].index(string.lower())
        return retValue
    except (ValueError, AttributeError):
        return string

def stateString2Int(string):
    try:
        retValue = ['offline', 'online', 'updating'].index(string.lower())
        return retValue
    except (ValueError, AttributeError):
        return string

def String2Float(string):
    try:
        retValue = float(string)
        return retValue
    except ValueError:
        return 0

class messagehandler:
    def __init__(self):
        self._db = None
        self._topic_parser = regexmatcher()
        self._topic_parser.registermatcher(
            r"^basetopic\/([0-9a-z-]+)\/\$system\/([0-9a-z]+)$", # basetopic/deviceid/$system/propertyid
            self.propertyhandler)
        self._topic_parser.registermatcher(
            r"^basetopic\/([0-9a-z-]+)\/([0-9a-z_]+)$", # basetopic/device/measurement
            self.measurementhandler)
        self._measurementExcludeList = ["ledcontroller1"]
        self._propertyExcludeList = ["uptime"]


    def setdatabase(self, db):
        self._db = db


    def onmessage(self, topic, payload):
        self._topic_parser.match(topic, payload.decode('utf8'))


    def _executequery(self, raw_sql, table, columns, values):
        try:
            cursor = self._db.conn().cursor()
            query = sql.SQL(raw_sql).format(
                        sql.Identifier(table),
                        sql.SQL(', ').join(map(sql.Identifier, columns)),
                        sql.SQL(', ').join(sql.Placeholder() * len(values)))
            #print(cursor.mogrify(query, values))
            cursor.execute(query, values)
            cursor.close
            self._db.conn().commit()
        except Exception as error:
            print(error)


    #def devicenamehandler(self, attributes, name):
    #    table = 'devices'
    #    columns = ('id', 'friendlyname')
    #    values = (attributes.group(1),
    #              name)
    #    query = """INSERT INTO {} ({}) VALUES ({}) 
    #               ON CONFLICT (id) do 
    #               UPDATE SET friendlyname = EXCLUDED.friendlyname;"""
    #    self._executequery(query, table, columns, values)


    #def loghandler(self, attributes, message):
    #    table = 'log'
    #    columns = ('time', 'deviceid', 'type', 'msg')
    #    if attributes.group(2) == 'logger':
    #        logtype = 'log'
    #    else:
    #        logtype = 'state'
    #    values = (datetime.now(),
    #              attributes.group(1),
    #              logtype,
    #              message)
    #    query = """INSERT INTO {} ({}) VALUES ({});"""
    #    self._executequery(query, table, columns, values)

    def propertyhandler(self, attributes, value):
        exist = self._propertyExcludeList.count( attributes.group(2))
        if (exist > 0):
            return
        value = boolString2Int(value)
        value = stateString2Int(value)
        value = String2Float(value)
        table = 'properties'
        columns = ('time',
                   'deviceid',
                   'propertyid',
                   'value')
        values = (datetime.now(),
                  attributes.group(1),
                  attributes.group(2),
                  value)
        query = """INSERT INTO {} ({}) VALUES ({});"""
        self._executequery(query, table, columns, values)



    def measurementhandler(self, attributes, value):
        exist = self._measurementExcludeList.count( attributes.group(1))
        if (exist > 0):
            return
        value = boolString2Int(value)
        value = String2Float(value)
        table = 'measurements'
        columns = ('time',
                   'deviceid',
                   'measurementid',
                   'value')
        values = (datetime.now(),
                  attributes.group(1),
                  attributes.group(2),
                  value)
        query = """INSERT INTO {} ({}) VALUES ({});"""
        self._executequery(query, table, columns, values)

