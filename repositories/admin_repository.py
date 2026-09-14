from database import get_connection, get_dict_cursor

class AdminRepository:
    def get_all_users(self):
        connection = get_connection()
        cursor = get_dict_cursor(connection)

        try:
            cursor.execute(
                """
                SELECT
                    user_id,
                    user_name,
                    name,
                    user_role,
                    active
                FROM users
                ORDER BY username
                """
            )

            return cursor.fetchall()

        finally:
            cursor.close()
            connection.close()

    def get_audit_logs(self):
        connection = get_connection()
        cursor = get_dict_cursor(connection)

        try: 
            cursor.execute(
                """
                SELECT
                    audit_log.audit_id,
                    audit_log.table_name,
                    audit_log.record_id,
                    audit_log.changed_at,
                    audit_log.old_values,
                    audit_log.new_values,
                    audit_log.reason,
                    users.username
                FROM audit_log
                JOIN users 
                ON users.user_id = audit_log.changed_by
                ORDER BY audit_log.changed_at DESC
                """
            )

            return cursor.fetchall()

        finally:
            cursor.close()
            connection.close()

    def reset_user_password(self, user_id, password_hash):
        connection = get_connection()
        cursor = get_dict_cursor(connection)

        try:
            cursor.execute(
                """
                UPDATE users
                SET
                    password_hash = %s,
                    must_change_password = TRUE
                WHERE user_id = %s
                """,
                (password_hash, user_id,)
            )

            connection.commit()

        except Exception:
            connection.rollback()
            raise

        finally:
            cursor.close()
            connection.close()

    def create_user(self, username, name, password_hash, role):
        connection = get_connection()
        cursor = connection.cursor()

        try: 
            cursor.execute(
                """
                INSERT INTO users
                (
                    username,
                    name,
                    password_hash,
                    user_role,
                    must_change_password,
                    active
                )
                VALUES 
                (%s,%s,%s,%s, TRUE, TRUE)
                """,
                (
                    username,
                    name,
                    password_hash,
                    role
                )
            )

            connection.commit()

        except Exception:
            connection.rollback()
            raise

        finally:
            cursor.close()
            connection.close()