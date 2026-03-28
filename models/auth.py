from db import get_connection

connection = get_connection()
cursor = connection.cursor()

def validate_user(username, password):
    try:
        sql = """
            SELECT * FROM users
            WHERE email = %s AND password = %s
        """
        cursor.execute(sql, (username, password))
        user = cursor.fetchone()
        return user
        
    except Exception as e:
        print(f"Error validating user: {e}")
        return None