from models.change_request import ChangeRequest
from database import get_connection, get_dict_cursor
from psycopg2 import sql

class ChangeRequestRepository:
    def create_request(self, change_request):
        connection = get_connection()
        cursor = connection.cursor()

        try:
            cursor.execute(
                """
                INSERT INTO change_requests
                (
                    requested_by,
                    table_name,
                    record_id,
                    field_name,
                    old_value,
                    new_value,
                    reason
                )
                VALUES
                (%s,%s,%s,%s,%s,%s,%s)
                """,
                (
                    change_request.requested_by,
                    change_request.table_name,
                    change_request.record_id,
                    change_request.field_name,
                    change_request.old_value,
                    change_request.new_value,
                    change_request.reason
                )
            )

            connection.commit()

        except Exception:
            connection.rollback()
            raise

        finally:
            cursor.close()
            connection.close()

    def get_products(self):
        connection = get_connection()
        cursor = get_dict_cursor(connection)

        try:
            cursor.execute(
                """
                SELECT
                    product_id,
                    product_name
                FROM products
                ORDER BY product_name
                """
            )

            return cursor.fetchall()

        finally:
            cursor.close()
            connection.close()

    def get_batches(self, product_id):
        connection = get_connection()
        cursor = get_dict_cursor(connection)

        try:
            cursor.execute(
                """
                SELECT
                    sample_id,
                    batch_nr
                FROM samples
                WHERE product_id = %s
                ORDER BY sample_id DESC
                """,
                (product_id,)
            )

            return cursor.fetchall()

        finally:
            cursor.close()
            connection.close()

    def get_test_records(
        self,
        table_name,
        id_column,
        sample_id
    ):
        connection = get_connection()
        cursor = get_dict_cursor(connection)

        try:
            query = sql.SQL(
                """
                SELECT
                    {id_column} AS record_id,
                    afterstorage_id
                FROM {table_name}
                WHERE sample_id = %s
                ORDER BY {id_column}
                """
            ).format(
                id_column=sql.Identifier(id_column),
                table_name=sql.Identifier(table_name)
            )

            cursor.execute(
                query,
                (sample_id,)
            )

            return cursor.fetchall()

        finally:
            cursor.close()
            connection.close()

    def get_test_fields(
        self,
        table_name,
        id_column,
        record_id,
        field_names
    ):
        connection = get_connection()
        cursor = get_dict_cursor(connection)

        try:
            columns = sql.SQL(", ").join(
                sql.Identifier(field)
                for field in field_names
            )

            query = sql.SQL(
                """
                SELECT {columns}
                FROM {table_name}
                WHERE {id_column} = %s
                """
            ).format(
                columns=columns,
                table_name=sql.Identifier(table_name),
                id_column=sql.Identifier(id_column)
            )

            cursor.execute(
                query,
                (record_id,)
            )

            return cursor.fetchone()

        finally:
            cursor.close()
            connection.close()

    def get_current_value(
        self,
        table_name,
        id_column,
        record_id,
        sample_id,
        field_name
    ):
        connection = get_connection()
        cursor = get_dict_cursor(connection)

        try:
            query = sql.SQL(
                """
                SELECT {field_name} AS current_value
                FROM {table_name}
                WHERE {id_column} = %s
                AND sample_id = %s
                """
            ).format(
                field_name=sql.Identifier(field_name),
                table_name=sql.Identifier(table_name),
                id_column=sql.Identifier(id_column)
            )

            cursor.execute(
                query,
                (
                    record_id,
                    sample_id
                )
            )

            result = cursor.fetchone()

            if result is None:
                return None

            return result["current_value"]

        finally:
            cursor.close()
            connection.close()

    def get_requests_by_user(self, user_id):
        connection = get_connection()
        cursor = get_dict_cursor(connection)

        try:
            cursor.execute(
                """
                SELECT
                    change_request_id,
                    table_name,
                    record_id,
                    field_name,
                    old_value,
                    new_value,
                    reason,
                    status,
                    requested_at,
                    reviewed_at,
                    review_comment
                FROM change_requests
                WHERE requested_by = %s
                ORDER BY requested_at DESC, change_request_id DESC
                """,
                (user_id,)
            )

            return cursor.fetchall()

        finally:
            cursor.close()
            connection.close()

    def get_pending_requests(self, reviewer_id):
        connection = get_connection()
        cursor = get_dict_cursor(connection)

        try:
            cursor.execute(
                """
                SELECT
                    change_request_id,
                    requested_by,
                    table_name,
                    record_id,
                    field_name,
                    old_value,
                    new_value,
                    reason,
                    status,
                    requested_at
                FROM change_requests
                WHERE status = 'pending'
                AND requested_by <> %s
                ORDER BY requested_at ASC
                """,
                (reviewer_id,)
            )

            return cursor.fetchall()

        finally:
            cursor.close()
            connection.close()

    def review_request(
        self,
        change_request_id,
        status,
        reviewed_by,
        review_comment
    ):
        connection = get_connection()
        cursor = connection.cursor()

        try:
            cursor.execute(
                """
                UPDATE change_requests
                SET
                    status = %s,
                    reviewed_by = %s,
                    reviewed_at = CURRENT_TIMESTAMP,
                    review_comment = %s
                WHERE change_request_id = %s
                AND status = 'pending'
                AND requested_by <> %s
                RETURNING change_request_id
                """,
                (
                    status,
                    reviewed_by,
                    review_comment,
                    change_request_id,
                    reviewed_by
                )
            )

            updated = cursor.fetchone()

            if updated is None:
                connection.rollback()
                return False

            connection.commit()

            return True

        except Exception:
            connection.rollback()
            raise

        finally:
            cursor.close()
            connection.close()