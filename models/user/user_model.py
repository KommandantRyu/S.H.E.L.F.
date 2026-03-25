from db import get_connection

connection = get_connection()
cursor = connection.cursor()

def get_user_profile(user_id):
    try:
        sql = "SELECT user_id, username, email, role, created_at FROM users WHERE user_id = %s"
        cursor.execute(sql,(user_id,))
        user = cursor.fetchone()
        if user:
            return {
                'user_id': user[0],
                'username': user[1],
                'email': user[2],
                'role': user[3],
                'created_at': user[4]
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
        cursor.execute(sql, params)
        connection.commit()
        
        if cursor.rowcount == 0:
            return False, "User not found"
        return True, "Profile updated successfully"
    except Exception as e:
        print(f"Error updating user profile: {e}")
        return False, "Database error occurred"

def get_user_borrowed_books(user_id):
    try:
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