from db import db_cursor

ALLOWED_USER_SORT_COLUMNS = {'user_id', 'username', 'email', 'created_at'}
DEFAULT_USER_SORT_COLUMN = 'user_id'
DEFAULT_USER_SORT_ORDER = 'ASC'

def get_all_users():
    try:
        with db_cursor() as cursor:
            cursor.execute("SELECT user_id, username, email, created_at FROM users")
            return cursor.fetchall()
    except Exception as e:
        print(f"Error fetching users: {e}")
        return None

def get_user_by_id(user_id):
    try:
        with db_cursor() as cursor:
            cursor.execute(
                "SELECT user_id, username, email, created_at FROM users WHERE user_id = %s",
                (user_id,),
            )
            return cursor.fetchone()
    except Exception as e:
        print(f"Error fetching user by ID: {e}")
        return None

def get_user_by_username(username):
    try:
        with db_cursor() as cursor:
            cursor.execute(
                "SELECT user_id, username, email, created_at FROM users WHERE username = %s",
                (username,),
            )
            return cursor.fetchone()
    except Exception as e:
        print(f"Error fetching user by username: {e}")
        return None

def create_user(name, email, password):
    try:
        with db_cursor() as cursor:
            cursor.execute(
                "SELECT user_id FROM users WHERE name = %s OR email = %s",
                (name, email),
            )
            if cursor.fetchone():
                return False, "Name or email already exists"

            sql = """
                INSERT INTO users (name, email, password)
                VALUES (%s, %s, %s)
            """
            cursor.execute(sql, (name, email, password))
            return True, "User created successfully"
    except Exception as e:
        print(f"Error creating user: {e}")
        return False, "Database error occurred"

def update_user(user_id, name=None, email=None, password=None):
    try:
        updates = []
        params = []
        
        if name:
            updates.append("username = %s")
            params.append(name)
        if email:
            updates.append("email = %s")
            params.append(email)
        if password:
            updates.append("password = %s")
            params.append(password)
        
        if not updates:
            return False, "No fields to update"
        
        params.append(user_id)
        sql = f"UPDATE users SET {', '.join(updates)} WHERE user_id = %s"
        with db_cursor() as cursor:
            cursor.execute(sql, params)
            if cursor.rowcount == 0:
                return False, "User not found"
            return True, "User updated successfully"
    except Exception as e:
        print(f"Error updating user: {e}")
        return False, "Database error occurred"

def delete_user(user_id):
    try:
        with db_cursor() as cursor:
            cursor.execute("DELETE FROM users WHERE user_id = %s", (user_id,))
            if cursor.rowcount == 0:
                return False, "User not found"
            return True, "User deleted successfully"
    except Exception as e:
        print(f"Error deleting user: {e}")
        return False, "Database error occurred"

def sort_users(sort_by=None, order=None):
    try:
        if not sort_by:
            sort_by = DEFAULT_USER_SORT_COLUMN
        if not order:
            order = DEFAULT_USER_SORT_ORDER

        sort_by = sort_by.lower()
        if sort_by not in ALLOWED_USER_SORT_COLUMNS:
            raise ValueError(f"Invalid sort column. Allowed: {ALLOWED_USER_SORT_COLUMNS}")

        order = order.upper()
        if order not in ('ASC', 'DESC'):
            raise ValueError("Sort order must be ASC or DESC")

        sql = f"SELECT user_id, username, email, created_at FROM users ORDER BY {sort_by} {order}"
        with db_cursor() as cursor:
            cursor.execute(sql)
            return cursor.fetchall()
    except Exception as e:
        print(f"Error fetching sorted users: {e}")
        return None
