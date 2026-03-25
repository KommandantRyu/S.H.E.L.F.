from flask import jsonify, flash
from db import get_connection
import string

connection = get_connection()
cursor = connection.cursor()


class user_services():
    def __init__(self,form):
        self.email = form.get("email")
        self.name = form.get("name")
        self.password = form.get("password")

    def duplicate_email(self):
       try:
           sql = "SELECT * FROM  users WHERE email = %s"
           cursor.execute(sql)
           dup = cursor.fetchone()
           return dup
       except Exception as e:
           return None
       
    def register(self, form):
        self.email = form.get("email")
        self.name = form.get("name")
        self.password = form.get("password")
        
class book_services():
    
    def __init__(self,form):
        self.title = form.get("title")
        self.author = form.get("author")
        self.genre = form.get("genre")
        self.yearpub = form.get("yearpub")
        self.pages = form.get("pages")
        self.isbn = form.get("isbn")

    def new_book(self,):
        try:
            sql = """
            INSERT INTO books(title, author, genre, year, pages, isbn) 
            VALUES (%s, %s, %s, %s, %s, %s)
            """
            cursor.execute(sql,(self.title, self.author, self.genre, self.yearpub, self.pages, self.isbn))
            connection.commit()
        
        except Exception as e:
            return [e]
        


           