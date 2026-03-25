from db import get_connection

connection = get_connection()
cursor = connection.cursor()

ALLOWED_USER_SORT_COLUMNS = {'user_id', 'username', 'email', 'role', 'created_at'}
DEFAULT_USER_SORT_COLUMN = 'user_id'
DEFAULT_USER_SORT_ORDER = 'ASC'

def get_all_users():
    try:
        cursor.execute("SELECT user_id, username, email, role, created_at FROM users")
        return cursor.fetchall()
    except Exception as e:
        print(f"Error fetching users: {e}")
        return None

def get_user_by_id(user_id):
    try:
        cursor.execute("SELECT user_id, username, email, role, created_at FROM users WHERE user_id = %s", (user_id,))
        return cursor.fetchone()
    except Exception as e:
        print(f"Error fetching user by ID: {e}")
        return None

def get_user_by_username(username):
    try:
        cursor.execute("SELECT user_id, username, email, role, created_at FROM users WHERE username = %s", (username,))
        return cursor.fetchone()
    except Exception as e:
        print(f"Error fetching user by username: {e}")
        return None

def create_user(username, email, password, role='user'):
    try:
        cursor.execute("SELECT user_id FROM users WHERE username = %s OR email = %s", (username, email))
        if cursor.fetchone():
            return False, "Username or email already exists"

        sql = """
            INSERT INTO users (username, email, password_hash, role)
            VALUES (%s, %s, %s, %s)
        """
        cursor.execute(sql, (username, email, password, role))
        connection.commit()
        return True, "User created successfully"
    except Exception as e:
        print(f"Error creating user: {e}")
        return False, "Database error occurred"

def update_user(user_id, username=None, email=None, password=None, role=None):
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
        if role:
            updates.append("role = %s")
            params.append(role)
        
        if not updates:
            return False, "No fields to update"
        
        params.append(user_id)
        sql = f"UPDATE users SET {', '.join(updates)} WHERE user_id = %s"
        cursor.execute(sql, params)
        connection.commit()
        
        if cursor.rowcount == 0:
            return False, "User not found"
        return True, "User updated successfully"
    except Exception as e:
        print(f"Error updating user: {e}")
        return False, "Database error occurred"

def delete_user(user_id):
    try:
        cursor.execute("DELETE FROM users WHERE user_id = %s", (user_id,))
        connection.commit()
        if cursor.rowcount == 0:
            return False, "User not found"
        return True, "User deleted successfully"
    except Exception as e:
        print(f"Error deleting user: {e}")
        return False, "Database error occurred"

def update_user_role(user_id, new_role):
    try:
        if new_role not in ('admin', 'user'):
            return False, "Invalid role. Allowed: admin, user"
        cursor.execute("UPDATE users SET role = %s WHERE user_id = %s", (new_role, user_id))
        connection.commit()
        if cursor.rowcount == 0:
            return False, "User not found"
        return True, f"User role updated to {new_role}"
    except Exception as e:
        print(f"Error updating user role: {e}")
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

        sql = f"SELECT user_id, username, email, role, created_at FROM users ORDER BY {sort_by} {order}"
        cursor.execute(sql)
        return cursor.fetchall()
    except Exception as e:
        print(f"Error fetching sorted users: {e}")
        return None