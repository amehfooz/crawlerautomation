HOST = 'localhost'
DB = 'carbyne'
USER = 'root'
PWD = 'wireless'

project_id = 'apps-1149'
service_account = 'naveed@apps-1149.iam.gserviceaccount.com'# Service account email       
json_key = 'sevice_key.json'# JSON key provided by Google

import mysql.connector
from bigquery import get_client

class DataBase(object):
    def __init__(self):
        try:
            self.conn = mysql.connector.connect(host=HOST, database=DB, user= USER, password = PWD)
        except Exception as e:
            print 'DB Connection Error'
            return

        query = """CREATE TABLE IF NOT EXISTS `scanTable` (
                `Name` Varchar(20) NOT NULL,
                `URL` Varchar(50) NOT NULL,
                `LastScanned` Date NOT NULL,
                `ScanStatus` Boolean,
                PRIMARY KEY (`URL`))
            """
        cursor = self.conn.cursor()

        cursor.execute(query)
    
    def populate(self, table):
        client = get_client(project_id, json_key_file=json_key, readonly=False)
        qry = "SELECT Name, Url  FROM [%s] LIMIT 10" % table

        try:
            job_id, results = client.query(qry, timeout=3000)

            results = client.get_query_rows(job_id)

            print results[0]
        except Exception as e:
            print e
            print 'timeout'

        
    def quit():
        self.conn.close()

db = DataBase()
db.populate("AppStore.GooglePlay_Master_DB")