from models.change_request import ChangeRequest
from database import get_connection, get_dict_cursor

class ChangeRequestRepository:
    def create_request(self, change_request):
        connection = get_connection()
        cursor = connection.cursor()

        try:
            cursor.execute(
                """
                INSERT INTO change_request
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