from db import db_cursor


class user_services():
    def __init__(self, form):
        self.email = form.get("email")
        self.name = form.get("name")
        self.password = form.get("password")

    def duplicate_email(self):
        try:
            with db_cursor() as cursor:
                sql = "SELECT * FROM users WHERE email = %s"
                cursor.execute(sql, (self.email,))
                return cursor.fetchone()
        except Exception as e:
            return None
       
    def register(self, form):
        self.email = form.get("email")
        self.name = form.get("name")
        self.password = form.get("password")
    
    def register_user(self, form, dup):
        if dup is None:
            try:
                with db_cursor() as cursor:
                    sql = """
                        INSERT INTO users (username, email, password_hash, role)
                        VALUES (%s, %s, %s, 'user')
                    """
                    cursor.execute(sql, (self.name, self.email, self.password))
            except Exception as e:
                print(f"Registration is Invalid: {e}")
                return None
            

class book_services():
    
    def __init__(self, form):
        self.title = form.get("title")
        self.author = form.get("author")
        self.genre = form.get("genre")
        self.yearpub = form.get("yearpub")
        self.pages = form.get("pages")
        self.isbn = form.get("isbn")

    def new_book(self):
        try:
            with db_cursor() as cursor:
                sql = """
                    INSERT INTO books(title, author, genre, year, pages, isbn, price)
                    VALUES (%s, %s, %s, %s, %s, %s, 0)
                """
                cursor.execute(
                    sql,
                    (self.title, self.author, self.genre, self.yearpub, self.pages, self.isbn),
                )
        except Exception as e:
            return [e]
