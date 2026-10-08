from database import get_dict_cursor, get_connection

class NotificationsRepository:
    def get_active_notifications(self, user_id):
        connection = get_connection()
        cursor = get_dict_cursor(connection)

        try:
            cursor.execute(
                """
                SELECT
                    notification_id,
                    notification_type,
                    title,
                    message,
                    reference_type,
                    reference_id,
                    link,
                    is_read,
                    created_at
                FROM notifications
                WHERE user_id = %s
                AND is_active = TRUE
                ORDER BY created_at DESC
                """,
                (user_id,)
            )

            return cursor.fetchall()

        finally:
            cursor.close()
            connection.close()

    def has_active_notifications(self, user_id):
        connection = get_connection()
        cursor = get_dict_cursor(connection)

        try:
            cursor.execute(
                """
                SELECT EXISTS (
                    SELECT 1
                    FROM notifications
                    WHERE user_id = %s
                    AND is_active = TRUE
                    AND read_at IS NULL
                ) AS has_notifications
                """,
                (user_id,)
            )

            result = cursor.fetchone()

            return result["has_notifications"]

        finally:
            cursor.close()
            connection.close()

    def create_notification(
            self,
            user_id,
            notification_type,
            title,
            message=None,
            reference_type=None,
            reference_id=None,
            link=None
    ):
        connection = get_connection()
        cursor = connection.cursor()

        try:
            cursor.execute(
                """
                INSERT INTO notifications
                (
                    user_id,
                    notification_type,
                    title,
                    message,
                    reference_type,
                    reference_id,
                    link
                )
                VALUES
                (%s,%s,%s,%s,%s,%s,%s)
                """,
                (
                    user_id,
                    notification_type,
                    title,
                    message,
                    reference_type,
                    reference_id,
                    link
                )
            )

            connection.commit()

        except Exception:
            connection.rollback()
            raise

        finally:
            cursor.close()
            connection.close()

    def close_notifications(self, reference_type, reference_id):
        connection = get_connection()
        cursor = connection.cursor()

        try:
            cursor.execute(
                """
                UPDATE notifications
                SET is_active = FALSE
                WHERE reference_type = %s
                AND reference_id = %s
                AND is_active = TRUE
                RETURNING notification_id
                """,
                (
                    reference_type,
                    reference_id
                )
            )

            updated = cursor.fetchall()

            connection.commit()

            return updated

        except Exception:
            connection.rollback()
            raise

        finally:
            cursor.close()
            connection.close()

    def get_other_users(self, exclude_user_id):
        connection = get_connection()
        cursor = get_dict_cursor(connection)

        try:
            cursor.execute(
                """
                SELECT
                    user_id,
                    name
                FROM users
                WHERE user_id <> %s
                ORDER BY name
                """,
                (exclude_user_id,)
            )

            return cursor.fetchall()

        finally:
            cursor.close()
            connection.close()

    def mark_notifications_read(self, user_id):
        connection = get_connection()
        cursor = connection.cursor()

        try:
            cursor.execute(
                """
                UPDATE notifications
                SET
                    is_read = TRUE,
                    read_at = CURRENT_TIMESTAMP
                WHERE user_id = %s
                AND is_read = FALSE
                """,
                (user_id,)
            )

            connection.commit()

        except Exception:
            connection.rollback()
            raise

        finally:
            cursor.close()
            connection.close()

    def has_unread_active_notifications(self, user_id):
        connection = get_connection()
        cursor = connection.cursor()

        try:
            cursor.execute(
                """
                SELECT EXISTS (
                    SELECT 1
                    FROM notifications
                    WHERE user_id = %s
                    AND is_active = TRUE
                    AND read_at IS NULL
                )
                """,
                (user_id,)
            )

            return cursor.fetchone()[0]

        finally:
            cursor.close()
            connection.close()

    def get_notification_summary(self, user_id):
        connection = get_connection()
        cursor = get_dict_cursor(connection)

        try:
            cursor.execute(
                """
                SELECT
                    notification_type,
                    COUNT(*) AS active_count,
                    COUNT(*) FILTER (
                        WHERE read_at IS NULL
                    ) AS unread_count,
                    MAX(created_at) AS latest_created_at
                FROM notifications
                WHERE user_id = %s
                AND is_active = TRUE
                GROUP BY notification_type
                ORDER BY latest_created_at DESC
                """,
                (user_id,)
            )

            return cursor.fetchall()

        finally:
            cursor.close()
            connection.close()