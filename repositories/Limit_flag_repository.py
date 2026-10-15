from psycopg2.extras import RealDictCursor
from database import get_connection, get_dict_cursor

class LimitFlagRepository:
    def open_or_update_flag(
            self,
            sample_id,
            test_key,
            test_stage,
            evaluation
    ):
        if evaluation["status"] != "outside":
            raise ValueError(
                "Alleen resultaten buiten limieten "
                "kunnen een limietmelding maken."
            )

        if (
            evaluation["limit_id"] is None
            or evaluation["value"] is None
        ):
            raise ValueError(
                "De evaluatie bevat onvoldoende gegevens."
            )

        field_name = evaluation["field_name"]

        connection = get_connection()
        cursor = connection.cursor()

        try:
            cursor.execute(
                """
                INSERT INTO limit_flags (
                    sample_id,
                    limit_id,
                    test_key,
                    field_name,
                    test_stage,
                    measured_value,
                    min_value,
                    max_value
                )
                VALUES
                (%s,%s,%s,%s,%s,%s,%s,%s)

                ON CONFLICT (
                    sample_id,
                    test_key,
                    field_name,
                    test_stage
                )
                WHERE status = 'open'
                DO NOTHING

                RETURNING limit_flag_id
                """,
                (
                    sample_id,
                    evaluation["limit_id"],
                    test_key,
                    field_name,
                    test_stage,
                    evaluation["value"],
                    evaluation["min_value"],
                    evaluation["max_value"]
                )
            )

            inserted = cursor.fetchone()

            if inserted is not None:
                flag_id = inserted[0]
                connection.commit()

                return {
                    "flag_id": flag_id,
                    "created": True
                }

            cursor.execute(
                """
                UPDATE limit_flags
                SET
                    limit_id = %s,
                    measured_value = %s,
                    min_value = %s,
                    max_value = %s,
                    last_evaluated_at = CURRENT_TIMESTAMP
                WHERE sample_id = %s
                    AND test_key = %s
                    AND field_name = %s
                    AND test_stage = %s
                    AND status = 'open'
                RETURNING limit_flag_id
                """,
                (
                    evaluation["limit_id"],
                    evaluation["value"],
                    evaluation["min_value"],
                    evaluation["max_value"],
                    sample_id,
                    test_key,
                    field_name,
                    test_stage
                )
            )

            updated = cursor.fetchone()

            if updated is None:
                raise RuntimeError(
                    "De bestaande limietmelding "
                    "kon niet worden bijgewerkt."
                )

            connection.commit()

            return {
                "flag_id": updated[0],
                "created": False
            }

        except Exception:
            connection.rollback()
            raise

        finally:
            cursor.close()
            connection.close()

    def resolve_flag(
            self,
            sample_id,
            test_key,
            field_name,
            test_stage,
            reason="Resultaat binnen limieten"
    ):
        connection = get_connection()
        cursor = connection.cursor()

        try:
            cursor.execute(
                """
                UPDATE limit_flags
                SET
                    status = 'resolved',
                    resolved_at = CURRENT_TIMESTAMP,
                    resolution_reason = %s,
                    last_evaluated_at = CURRENT_TIMESTAMP
                WHERE sample_id = %s
                    AND test_key = %s
                    AND field_name = %s
                    AND test_stage = %s
                    AND status = 'open'
                RETURNING limit_flag_id
                """,
                (
                    reason,
                    sample_id,
                    test_key,
                    field_name,
                    test_stage
                )
            )

            result = cursor.fetchone()

            connection.commit()

            return result[0] if result else None

        except Exception:
            connection.rollback()
            raise

        finally:
            cursor.close()
            connection.close()

    def get_open_flags(self):
        connection = get_connection()
        cursor = connection.cursor(cursor_factory=RealDictCursor)

        try:
            cursor.execute(
                """
                SELECT
                    lf.limit_flag_id,
                    lf.sample_id,
                    s.batch_nr,
                    l.product_id,
                    lf.test_key,
                    lf.field_name,
                    lf.measured_value,
                    lf.min_value,
                    lf.max_value,
                    lf.status,
                    lf.detected_at
                FROM limit_flags AS lf
                JOIN samples AS s
                    ON s.sample_id = lf.sample_id
                JOIN limits AS l
                    ON l.limit_id = lf.limit_id
                WHERE lf.status = 'open'
                ORDER BY lf.detected_at DESC
                """
            )

            return cursor.fetchall()
        
        finally:
            cursor.close()
            connection.close()

    def get_flag_by_id(self, flag_id):
        connection = get_connection()
        cursor = connection.cursor(cursor_factory=RealDictCursor)

        try:
            cursor.execute(
                """
                SELECT *
                FROM limit_flags
                WHERE limit_flag_id = %s
                """,
                (flag_id,)
            )

            return cursor.fetchone()

        finally:
            cursor.close()
            connection.close()