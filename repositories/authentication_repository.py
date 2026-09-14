from database import get_connection, get_dict_cursor

class AuthenticationRepository:
    def get_active_users_by_username(self, username):
        connection = get_connection
        cursor = get_dict_cursor(connection)

        try:
            cursor.execute(
                """
                SELECT * 
                FROM users
                WHERE LOWER(username) = LOWER(%s)
                AND active = TRUE
                """,
                (username,)
            )

            return cursor.fetchall()

        finally: 
            cursor.close()
            connection.close()

    def update_password(self, user_id, passwaord_hash):
        connection = get_connection()
        cursor = get_dict_cursor(connection)

        try:
            cursor.execute(
                """
                UPDATE users
                SET 
                    password_hash = %s
                    must_change_password = FALSE
                WHERE user_id = %s
                """,
                (passwaord_hash, user_id,)
            )

            connection.commit()

        except Exception:
            connection.rollback()
            raise

        finally:
            cursor.close()
            connection.close()

            