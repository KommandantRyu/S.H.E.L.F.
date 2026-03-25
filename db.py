import pymysql

def get_connection():
   return pymysql.connect(
        host="localhost",
        user="root",
        password="G@briel110406",
        database="library_db",
        cursorclass=pymysql.cursors.DictCursor,
        autocommit=True,
    )