from models.skinformation import skinformationresult
from database import get_connection, get_dict_cursor

class SkinformationRepository:
    def add_result(self, result: skinformationresult):
        connection = get_connection()
        cursor = connection.cursor()

        try:
            cursor.execute(
                """
                INSERT INTO skinformation
                (
                    sample_id,
                    afterstorage_id,
                    operator_id,
                    remark,
                    skinformation_time,
                    temp_skinformation_time,
                    rh_skinformation_time,
                    tack_free_time,
                    temp_tack_free_time,
                    rh_tack_free_time
                )
                VALUES
                (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                """,
                (
                    result.sample_id,
                    result.afterstorage_id,
                    result.operator_id,
                    result.remark,
                    result.skinformation_time,
                    result.temp_skinformation_time,
                    result.rh_skinformation_time,
                    result.tack_free_time,
                    result.temp_tack_free_time,
                    result.rh_tack_free_time
                ),
            )

            connection.commit()

        except Exception: 
            connection.rollback()
            raise

        finally:
            cursor.close()
            connection.close()