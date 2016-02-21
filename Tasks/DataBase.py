HOST = 'localhost'
DB = 'carbyne'
USER = 'root'
PWD = 'wireless'

project_id = 'apps-1149'
service_account = 'naveed@apps-1149.iam.gserviceaccount.com'# Service account email       
json_key = 'sevice_key.json'# JSON key provided by Google

import sys
sys.path.insert(0, 'libs')

import mysql.connector
from bigquery import get_client

class DataBase(object):
    def __init__(self, scantable):
        try:
            self.conn = mysql.connector.connect(host=HOST, database=DB, user= USER, password = PWD)
        except Exception as e:
            print 'DB Connection Error'
            return

        self.scantable = scantable
        query = """CREATE TABLE IF NOT EXISTS `%s` (
                `Name` Varchar(20) NOT NULL,
                `URL` Varchar(120) NOT NULL,
                `LastScanned` Date DEFAULT NULL,
                `ScanStatus` Boolean Default FALSE,
                PRIMARY KEY (`URL`))
            """ % self.scantable
        cursor = self.conn.cursor()

        cursor.execute(query)

    def populate(self, table):
        client = get_client(project_id, json_key_file=json_key, readonly=False)
        qry = "SELECT Name, Url  FROM [%s] LIMIT 10" % table

        try:
            job_id, results = client.query(qry, timeout=3000)

            results = client.get_query_rows(job_id)

            for row in results:
                query = """
                INSERT INTO %s (Name, URL) VALUES ('%s', '%s')
                ON DUPLICATE KEY UPDATE URL = '%s'
                """ % (self.scantable, row['Name'].replace('\'', ''), row['Url'], row['Url'])
                
                cursor = self.conn.cursor()
                cursor.execute(query)

            self.conn.commit()
        except Exception as e:
            print e
            print 'timeout'

        print "Populated Table"
        
    def toCrawl(self):
        query = """SELECT URL FROM %s WHERE ScanStatus = FALSE OR LastScanned < DATE_SUB(NOW(), Interval 31 DAY)""" % self.scantable

        cursor = self.conn.cursor()
        cursor.execute(query)

        results = cursor.fetchall()

        urls = [row[0] for row in results]

        return urls

    def updateStatus(self, urls):
        urls = [(x, 0) for x in urls]
        query = ""
        if self.scantable == 'GooglePlay':
            query = """UPDATE GooglePlay SET ScanStatus = TRUE, LastScanned = NOW() WHERE URL = %s OR 1 = %s"""
        elif self.scantable == 'AppStore':
            query = """UPDATE AppStore SET ScanStatus = TRUE, LastScanned = NOW() WHERE URL = %s OR 1 = %s"""
        elif self.scantable == 'Windows':
            query = """UPDATE Windows SET ScanStatus = TRUE, LastScanned = NOW() WHERE URL = %s OR 1 = %s"""
        cursor = self.conn.cursor()
        cursor.executemany(query, urls)

        self.conn.commit()
        print "UPDATED TABLE"
        
    def quit(self):
        self.conn.close()