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
            self.cursor = self.conn.cursor(buffered=True) # should add buffered=True
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
            print("[AzureDBHandler.Query] Error Code: {}".format(err))

    def Select(self, statement):
        try:
            self.cursor.execute(statement)
            row = self.cursor.fetchone()
            return row[0]
            # rows = self.cursor.fetchone()
            # for i in range(len(rows)):
            #     print(rows[i])
        except mysql.connector.Error as err:
            print("[AzureDBHandler.Select] Error Code: {}".format(err))
            
    def GetColumn(self, statement):
        try:
            self.cursor.execute(statement)
            num_fields = len(self.cursor.description)
            field_names = [i[0] for i in self.cursor.description]
            return field_names
        except mysql.connector.Error as err:
            print("[AzureDBHandler.Select] Error Code: {}".format(err))

    def SelectAll(self, statement):
        try:
            dict_list = []
            self.cursor.execute(statement)
            self.conn.commit()
            num_fields = len(self.cursor.description)
            # Get column
            field_names = [i[0] for i in self.cursor.description]
            row = self.cursor.fetchall()
            # Zip column into each rows
            [dict_list.append(dict(zip(field_names, (i)))) for i in row]
            # Return dict list type
            return dict_list

        except mysql.connector.Error as err:
            print("[AzureDBHandler.Select] Error Code: {}".format(err))

    def Update(self, statement):
        try:
            self.cursor.execute(statement)
            self.conn.commit()
        except mysql.connector.Error as err:
            print("[AzureDBHandler.Update] Error Code: {}".format(err))

    def Insert(self, statement):
        try:
            self.cursor.execute(statement)
            self.conn.commit()
        except mysql.connector.Error as err:
            print("[AzureDBHandler.Insert] Error Code: {}".format(err))

    def Delete(self, statement):
        try:
            self.cursor.execute(statement)
            self.conn.commit()
        except mysql.connector.Error as err:
            print("[AzureDBHandler.Insert] Error Code: {}".format(err))
        
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
