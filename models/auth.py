from db import get_connection

connection = get_connection()
cursor = connection.cursor()

def validate_user(username, password):
    try:
        sql = """
            SELECT user_id, username, email, role
            FROM users
            WHERE username = %s AND password_hash = %s
        """
        cursor.execute(sql, (username, password))
        user = cursor.fetchone()
        
        if user:
            return {
                'user_id': user[0],
                'username': user[1],
                'email': user[2],
                'role': user[3]
            }
        return None
    except Exception as e:
        print(f"Error validating user: {e}")
        return None