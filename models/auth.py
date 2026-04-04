from db import db_cursor


def validate_user(email, password):
    try:
        with db_cursor() as cursor:
            sql = """
                SELECT user_id, username, email, created_at FROM users
                WHERE email = %s AND password = %s
            """
            cursor.execute(sql, (email, password))
            return cursor.fetchone()
    except Exception as e:
        print(f"Error validating user: {e}")
        return None
