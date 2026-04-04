from db import db_cursor


def get_user_profile(user_id):
    try:
        with db_cursor() as cursor:
            sql = "SELECT user_id, username, email, role, created_at FROM users WHERE user_id = %s"
            cursor.execute(sql, (user_id,))
            user = cursor.fetchone()
            if user:
                return {
                    'user_id': user['user_id'],
                    'username': user['username'],
                    'email': user['email'],
                    'role': user['role'],
                    'created_at': user['created_at']
                }
            return None
    except Exception as e:
        print(f"Error fetching user profile: {e}")
        return None

def update_user_profile(user_id, username=None, email=None, password=None):
    try:
        updates = []
        params = []
        
        if username:
            updates.append("username = %s")
            params.append(username)
        if email:
            updates.append("email = %s")
            params.append(email)
        if password:
            updates.append("password_hash = %s")
            params.append(password)
        
        if not updates:
            return False, "No fields to update"
        
        params.append(user_id)
        sql = f"UPDATE users SET {', '.join(updates)} WHERE user_id = %s"
        with db_cursor() as cursor:
            cursor.execute(sql, params)
            if cursor.rowcount == 0:
                return False, "User not found"
            return True, "Profile updated successfully"
    except Exception as e:
        print(f"Error updating user profile: {e}")
        return False, "Database error occurred"

def get_user_borrowed_books(user_id):
    try:
        with db_cursor() as cursor:
            sql = """
                SELECT b.book_id, b.title, b.author, b.genre, b.year, b.pages, b.isbn,
                       bb.borrow_date, bb.due_date, bb.return_date
                FROM borrowed_books bb
                JOIN books b ON bb.book_id = b.book_id
                WHERE bb.user_id = %s AND bb.return_date IS NULL
                ORDER BY bb.borrow_date DESC
            """
            cursor.execute(sql, (user_id,))
            return cursor.fetchall()
    except Exception as e:
        print(f"Error fetching borrowed books: {e}")
        return None

def get_user_borrowing_history(user_id):
    try:
        with db_cursor() as cursor:
            sql = """
                SELECT b.book_id, b.title, b.author, b.genre, b.year, b.pages, b.isbn,
                       bb.borrow_date, bb.due_date, bb.return_date
                FROM borrowed_books bb
                JOIN books b ON bb.book_id = b.book_id
                WHERE bb.user_id = %s
                ORDER BY bb.borrow_date DESC
            """
            cursor.execute(sql, (user_id,))
            return cursor.fetchall()
    except Exception as e:
        print(f"Error fetching borrowing history: {e}")
        return None

def get_user_purchased_books(user_id):
    try:
        with db_cursor() as cursor:
            sql = """
                SELECT b.book_id, b.title, b.author, b.genre, b.year, b.pages, b.isbn,
                       pb.purchase_date, pb.price_paid
                FROM purchased_books pb
                JOIN books b ON pb.book_id = b.book_id
                WHERE pb.user_id = %s
                ORDER BY pb.purchase_date DESC
            """
            cursor.execute(sql, (user_id,))
            return cursor.fetchall()
    except Exception as e:
        print(f"Error fetching purchased books: {e}")
        return None
    
def register_user(name, email, password):
    """Register a new user. `name` maps to username in the database."""
    try:
        with db_cursor() as cursor:
            cursor.execute(
                "SELECT user_id FROM users WHERE email = %s OR username = %s",
                (email, name),
            )
            if cursor.fetchone():
                return False, "Email or username already registered"

            sql = """
                INSERT INTO users (username, email, password_hash, role)
                VALUES (%s, %s, %s, 'user')
            """
            cursor.execute(sql, (name, email, password))
            return True, "Registration successful"
    except Exception as e:
        print(f"Error registering user: {e}")
        return False, "Database error occurred"
