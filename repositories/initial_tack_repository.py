from models.initial_tack import InitialTackResult
from database import get_connection, get_dict_cursor

class InitialTackRepository:
    def add_result(self, result: InitialTackResult, initial_tack: float):
        connection = get_connection()
        cursor = connection.cursor()

        try:
            cursor.execute(
                """
                INSERT INTO initial_tack
                (
                    sample_id,
                    operator_id,
                    remark,
                    area,
                    area_weight,
                    added_weight,
                    humidity,
                    initial_tack
                )
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
                """,
                (  
                    result.sample_id,
                    result.operator_id,
                    result.remark,
                    result.area,
                    result.area_weight,
                    result.added_weight,
                    result.humidity,
                    initial_tack,
                )
            )

            connection.commit()

        except Exception:
            connection.rollback()
            raise

        finally:
            cursor.close()
            connection.close()

    def get_required_products(self):
        connection = get_connection()
        cursor = get_dict_cursor(connection)

        try:
            cursor.execute(
                """
                SELECT
                    products.product_id,
                    products.product_name
                FROM products
                JOIN product_test_requirements
                ON product_test_requirements.product_id = products.product_id
                WHERE product_test_requirements.test_type_id = 8
                ORDER BY products.product_name 
                """
            )

            return cursor.fetchall()

        finally:
            cursor.close()
            connection.close()

    def get_latest_results(self, limit=25):
        connection = get_connection()
        cursor = get_dict_cursor(connection)

        try:
            cursor.execute(
                """
                SELECT
                    samples.batch_nr,
                    initial_tack.area,
                    initial_tack.area_weight,
                    initial_tack.added_weight,
                    initial_tack.initial_tack,
                    initial_tack.humidity
                FROM initial_tack
                JOIN samples
                ON samples.sample_id = initial_tack.sample_id
                ORDER BY initial_tack.initial_tack_id DESC
                LIMIT %s
                """,
                (limit,),
            )

            return cursor.fetchall()

        finally:
            cursor.close()
            connection.close()

    def get_available_samples(self, product_id):
        connection = get_connection()
        cursor = get_dict_cursor(connection)

        try:
            cursor.execute(
                """
                SELECT
                    samples.sample_id,
                    samples.batch_nr AS display_name
                FROM samples
                LEFT JOIN initial_tack
                ON initial_tack.sample_id = samples.sample_id
                WHERE samples.product_id = %s
                AND samples.prod_date <= CURRENT_DATE - 7
                AND MOD(
                    samples.batch_sequence,
                    (
                        SELECT frequency
                        FROM product_test_requirements
                        WHERE product_id = samples.product_id
                        AND test_type_id = 8    
                    )
                ) = 0
                AND initial_tack.sample_id IS NULL
                ORDER BY samples.sample_id
                """,
                (product_id,)
            )

            return cursor.fetchall()

        finally:
            cursor.close()
            connection.close()