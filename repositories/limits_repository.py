from decimal import Decimal, InvalidOperation
from psycopg2.extras import RealDictCursor
from database import get_dict_cursor, get_connection

class LimitsRepository:
    @staticmethod
    def _validate_values(min_value, max_value):
        try:
            minimum = (
                Decimal(str(min_value))
                if min_value not in (None, "")
                else None
            )

            maximum = (
                Decimal(str(max_value))
                if max_value not in (None, "")
                else None
            )

        except (InvalidOperation, ValueError, TypeError):
            raise ValueError(
                "Minimum en Maximum moeten geldige getallen zijn."
            )

        if minimum is None and maximum is None:
            raise ValueError(
                "Vul minimaal een minimum of maximum in."
            )

        if (
            (minimum is not None and not minimum.is_finite())
            or (maximum is not None and not maximum.is_finite())
        ):
            raise ValueError(
                "Minimum en maximum moeten eindige getallen zijn."
            )

        if (
            minimum is not None
            and maximum is not None
            and minimum > maximum
        ):
            raise ValueError(
                "Minimum mag niet hoger zijn dan maximum"
            )

        return minimum, maximum

    def het_product_limits(
            self, 
            product_id,
            include_inactive=False
    ):
        connection = get_connection()
        cursor = get_dict_cursor(connection)

        try:
            query = """
                SELECT 
                    limit_id,
                    product_id,
                    test_key,
                    field_name,
                    test_stage,
                    min_value,
                    max_value,
                    is_active,
                    created_by,
                    created_at
                FROM limits
                WHERE product_id = %s
            """

            if not include_inactive:
                query += " AND is_active = TRUE"

            query = """
            ORDER BY
                test_key,
                field_name,
                test_stage,
                created_at DESC,
                limit_id DESC
            """

            cursor.execute(query, (product_id,))

            return cursor.fetchall

        finally:
            cursor.close()
            connection.close()

    def get_active_limit(
            self,
            product_id,
            test_key,
            field_name,
            test_stage="initial"
    ):
        connection = get_connection()
        cursor = get_dict_cursor(connection)

        try:
            cursor.execute(
                """
                SELECT *
                FROM limits
                WHERE product_id = %s
                AND test_key = %s
                AND field_name = %s
                AND test_stage = %s
                AND is_active = TRUE
                """,
                (
                    product_id,
                    test_key,
                    field_name,
                    test_stage
                )
            )

            return cursor.fetchone()

        finally:
            cursor.close()
            connection.close()

    def get_limit_by_id(self, limit_id):
        connection = get_connection()
        cursor = connection.cursor(cursor_factory=RealDictCursor)

        try:
            cursor.execute(
                """
                SELECT *
                FROM limits
                WHERE limit_id = %s
                """,
                (limit_id,)
            )

            return cursor.fetchone()

        finally:
            cursor.close()
            connection.close()

    def create_limit(
            self,
            product_id,
            test_key,
            field_name,
            test_stage,
            min_value,
            max_value,
            created_by
    ):
        minimum, maximum = self._validate_values(min_value, max_value)

        connection = get_connection()
        cursor = connection.cursor()

        try:
            cursor.execute(
                """
                INSERT INTO limits (
                    product_id,
                    test_key,
                    field_name,
                    test_stage,
                    min_value,
                    max_value,
                    created_by
                )
                VALUES
                (%s,%s,%s,%s,%s,%s,%s)
                RETURNING limit_id
                """,
                (
                    product_id,
                    test_key,
                    field_name,
                    test_stage,
                    min_value,
                    max_value,
                    created_by
                )
            )

            limit_id = cursor.fetchone()[0]
            connection.commit()

            return limit_id

        except Exception:
            connection.rollback()
            raise

        finally:
            cursor.close()
            connection.close()

    def deactivate_limit(self, limit_id):
        connection = get_connection()
        cursor = connection.cursor()

        try:
            cursor.execute(
                """
                UPDATE limits
                set is_active = FALSE
                WHERE limit_id = %s
                AND is_active = TRUE
                """,
                (limit_id,)
            )

            succes = cursor.rowcount > 0
            connection.commit()

            return succes

        except Exception:
            connection.rollback()
            raise

        finally:
            cursor.close()
            connection.close()

    def replace_limit(
            self,
            limit_id,
            min_value,
            max_value,
            created_by
    ):
        minimum, maximum = self._validate_values(min_value, max_value)

        connection = get_connection()
        cursor = connection.cursor(cursor_factory=RealDictCursor)

        try:
            cursor.execute(
                """
                UPDATE limits
                SET is_active = FALSE
                WHERE limit_id = %s
                AND is_active = TRUE
                RETURNING 
                    product_id,
                    test_key,
                    field_name,
                    test_stage
                """,
                (limit_id)
            )

            old_limit = cursor.fetchone()

            if old_limit is None:
                raise ValueError(
                    "De limiet bestaat niet of is al inactief."
                )

            cursor.execute(
                """
                INSERT INTO limits (
                    product_id,
                    test_key,
                    field_name,
                    test_stage,
                    min_value,
                    max_value,
                    created_by
                )
                VALUES
                (%s,%s,%s,%s,%s,%s,%s)
                RETURNING limit_id
                """,
                (
                    old_limit["product_id"],
                    old_limit["test_key"],
                    old_limit["field_name"],
                    old_limit["test_stage"],
                    minimum,
                    maximum,
                    created_by
                )
            )

            new_limit_id = cursor.fetchone()["limit_id"]
            connection.commit()

            return new_limit_id

        except Exception:
            connection.rollback()
            raise

        finally:
            cursor.close()
            connection.close()