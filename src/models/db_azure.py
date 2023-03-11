import mysql.connector
from mysql.connector import errorcode
import time

class AzureDB():
    def __init__(self, cfg):
        self.config = cfg
        self.Connect()

    def Connect(self):
        #connect to db
        try:
            self.conn = mysql.connector.connect(**self.config)
            print("Connection established")
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                print("Something is wrong")
            elif err.errno == errorcode.ER_BAD_DB_ERROR:
                print("Database does not exist")
            else:
                print(err)
        else:
            self.cursor = self.conn.cursor()
            print('cursor connect')

    def Disconnect(self):
        # Cleanup
        self.cursor.close()
        self.conn.close()
        print("Database Disconnected")

    def Query(self, statement):
        try:
            self.cursor.execute(statement)
            self.conn.commit()
        except mysql.connector.Error as err:
            print("[AzureDBHandler] Error Code: {}".format(err))

    def FetchOne(self, statement):
        # Read data
        self.cursor.execute(statement)
        rows = self.cursor.fetchone()
        for i in range(len(rows)):
            print(rows[i])
        
if __name__ == '__main__':

    statement = "CREATE TABLE inventory (id serial PRIMARY KEY, name VARCHAR(50), quantity INTEGER);"
    statement2 = "INSERT INTO inventory (id, name, quantity) VALUES (8, 'apple', 110);"
    quantity = 304
    id = 8
    statement3 = f'UPDATE inventory SET quantity = {quantity} WHERE id = {id};'
    nwdb = AzureDB()
    # nwdb.Connect()
    nwdb.Query(statement3)
    time.sleep(2)
    # nwdb.Disconnect()
