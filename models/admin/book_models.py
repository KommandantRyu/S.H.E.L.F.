from db import get_connection

connection = get_connection()
cursor = connection.cursor()

ALLOWED_SORT_COLUMNS = {'book_id', 'title', 'author', 'genre', 'year', 'pages', 'isbn'}
DEFAULT_SORT_COLUMN = 'title'
DEFAULT_SORT_ORDER = 'ASC'

def get_all_books():
    try:
        cursor.execute("SELECT * FROM books")
        books = cursor.fetechall()
        return books
    except Exception as e:
        print(f"Error fetching books: {e}")
        return None

def get_book_by_title(title):
    try:
        cursor.execute("SELECT * FROM books WHERE title = %s", (title,))
        return cursor.fetchone()
    except Exception as e:
        print(f"Error fetching book by title: {e}")
        return None

def update_book(book_id, title, author, genre, year, pages, isbn):
    try:
        sql = """
            UPDATE books SET
            title = %s, author = %s, genre = %s, year = %s, pages = %s, isbn = %s
            WHERE book_id = %s
        """
        cursor.execute(sql, (title, author, genre, year, pages, isbn, book_id))
        connection.commit()
        return True
    except Exception as e:
        print(f"Error updating book: {e}")
        return False

def delete_book(book_id):
    try:
        cursor.execute("DELETE FROM books WHERE book_id = %s", (book_id,))
        connection.commit()
        return True
    except Exception as e:
        print(f"Error deleting book: {e}")
        return False

def sort_books(sort_by=None, order=None):
    try:
        if not sort_by:
            sort_by = DEFAULT_SORT_COLUMN
        if not order:
            order = DEFAULT_SORT_ORDER

        sort_by = sort_by.lower()
        if sort_by not in ALLOWED_SORT_COLUMNS:
            raise ValueError(f"Invalid sort column. Allowed: {ALLOWED_SORT_COLUMNS}")

        order = order.upper()
        if order not in ('ASC', 'DESC'):
            raise ValueError("Sort order must be ASC or DESC")

        sql = f"SELECT * FROM books ORDER BY {sort_by} {order}"
        cursor.execute(sql)
        return cursor.fetchall()
    except Exception as e:
        print(f"Error fetching sorted books: {e}")
        return None

def borrow_book(book_id, user_id, borrow_date, due_date):
    try:
        cursor.execute("SELECT * FROM books WHERE book_id = %s", (book_id,))
        book = cursor.fetchone()
        if not book:
            return False, "Book not found"

        cursor.execute(
            "SELECT * FROM borrowed_books WHERE book_id = %s AND return_date IS NULL",
            (book_id,)
        )
        active_borrow = cursor.fetchone()
        if active_borrow:
            return False, "Book is already borrowed"

        sql = """
            INSERT INTO borrowed_books (book_id, user_id, borrow_date, due_date, return_date)
            VALUES (%s, %s, %s, %s, NULL)
        """
        cursor.execute(sql, (book_id, user_id, borrow_date, due_date))
        connection.commit()
        return True, "Book borrowed successfully"
    except Exception as e:
        print(f"Error borrowing book: {e}")
        return False, "Database error occurred"

def return_book(book_id, return_date):
    try:
        cursor.execute(
            "UPDATE borrowed_books SET return_date = %s WHERE book_id = %s AND return_date IS NULL",
            (return_date, book_id)
        )
        if cursor.rowcount == 0:
            return False, "No active borrow found for this book"
        connection.commit()
        return True, "Book returned successfully"
    except Exception as e:
        print(f"Error returning book: {e}")
        return False, "Database error occurred"

def purchase_book(book_id, user_id, purchase_date, price_paid):
    try:
        cursor.execute("SELECT * FROM books WHERE book_id = %s", (book_id,))
        book = cursor.fetchone()
        if not book:
            return False, "Book not found"

        sql = """
            INSERT INTO purchased_books (book_id, user_id, purchase_date, price_paid)
            VALUES (%s, %s, %s, %s)
        """
        cursor.execute(sql, (book_id, user_id, purchase_date, price_paid))
        connection.commit()
        return True, "Book purchased successfully"
    except Exception as e:
        print(f"Error purchasing book: {e}")
        return False, "Database error occurred"
    
def get_book_by_id(book_id):
    try:
        cursor.execute("SELECT * FROM books WHERE book_id = %s", (book_id,))
        return cursor.fetchone()
    except Exception as e:
        print(f"Error fetching book by ID: {e}")
        return None

def create_book(title, author, genre, year, pages, isbn):
    try:
        sql = """
            INSERT INTO books (title, author, genre, year, pages, isbn)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        cursor.execute(sql, (title, author, genre, year, pages, isbn))
        connection.commit()
        return True, "Book created successfully"
    except Exception as e:
        print(f"Error creating book: {e}")
        return False, "Database error occurred"
