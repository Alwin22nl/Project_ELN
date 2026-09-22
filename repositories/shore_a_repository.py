from models.shore_a import ShoreAPrepResult, ShoreATestResult
from database import get_connection, get_dict_cursor

class ShoreARepository:
    def add_prep_result(self, result: ShoreAPrepResult):
        connection = get_connection()
        cursor = connection.cursor()

        try: 
            cursor.execute(
                """
                INSERT INTO shore_a_preparation
                (
                    sample_id,
                    operator_id,
                    remark
                )
                VALUES
                (%s,%s,%s)
                """,
                (
                    result.sample_id,
                    result.operator_id,
                    result.remark,
                )
            )

            connection.commit()

        except Exception:
            connection.rollback()
            raise

        finally:
            cursor.close()
            connection.close()

    def submit_test_result(self, result: ShoreATestResult, shore_a_avg: float):
        connection = get_connection()
        cursor = connection.cursor()

        try:
            cursor.execute(
                """
                INSERT INTO shore_a
                (
                    sample_id,
                    operator_id,
                    remark,
                    shore_a_1,
                    shore_a_2,
                    shore_a_3,
                    shore_a_avg,
                    temperature,
                    humidity
                )
                VALUES
                (%s,%s,%s,%s,%s,%s,%s,%s,%s)
                """,
                (
                    result.sample_id,
                    result.operator_id,
                    result.remark,
                    result.shore_a_1,
                    result.shore_a_2,
                    result.shore_a_3,
                    shore_a_avg,
                    result.temperature,
                    result.humidity
                )
            )

            connection.commit()

        except Exception:
            connection.rollback()
            raise

        finally:
            cursor.close()
            connection.close()

    def get_samples_for_prep(self, product_id):
        connection = get_connection()
        cursor = get_dict_cursor(connection)

        try:
            cursor.execute(
                """
                SELECT
                    samples.sample_id,
                    samples.batch_nr AS display_name,
                    products.product_name
                FROM samples
                JOIN products
                ON products.product_id = samples.product_id
                JOIN product_test_requirements
                ON product_test_requirements.product_id = products.product_id
                LEFT JOIN shore_a_preparation AS shore_a_prep
                ON shore_a_prep.sample_id = samples.sample_id
                WHERE product_test_requirements.test_type_id = 3
                AND samples.product_id = %s
                AND shore_a_prep.sample_id IS NULL
                AND samples.prod_date <= CURRENT_DATE - 7
                AND
                (
                    samples.batch_sequence = 1
                    OR
                    MOD(
                        samples.batch_sequence,
                        product_test_requirements.frequency
                    ) = 0
                )
                ORDER BY samples.product_id, samples.sample_id;
                """,
                (product_id,)
            )

            return cursor.fetchall()

        finally:
            cursor.close()
            connection.close()

    def get_samples_for_test(self, product_id):
        connection = get_connection()
        cursor = get_dict_cursor(connection)

        try:
            cursor.execute(
                """
                SELECT
                    samples.sample_id,
                    samples.batch_nr AS display_name
                FROM shore_a_preparation AS shore_a_prep
                JOIN samples
                ON samples.sample_id = shore_a_prep.sample_id
                LEFT JOIN shore_a
                ON shore_a.sample_id = samples.sample_id
                WHERE samples.product_id = %s
                AND shore_a.sample_id IS NULL
                AND shore_a_prep.prepared_date::date <= CURRENT_DATE - INTERVAL '7 days'
                ORDER BY samples.product_id, samples.sample_id;
                """,
                (product_id,)
            )

            return cursor.fetchall()

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
                WHERE product_test_requirements.test_type_id = 3
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
                    shore_a.shore_a_1,
                    shore_a.shore_a_2,
                    shore_a.shore_a_3,
                    shore_a.shore_a_avg,
                    shore_a.temperature,
                    shore_a.humidity
                FROM shore_a
                JOIN samples
                ON samples.sample_id = shore_a.sample_id
                ORDER BY shore_a.shore_a_id DESC
                LIMIT %s
                """,
                (limit,),
            )

            return cursor.fetchall()

        finally:
            cursor.close()
            connection.close()

    def get_prep_list(self):
        connection = get_connection()
        cursor = get_dict_cursor(connection)

        try:   
            cursor.execute(
                """
                SELECT 
                    samples.batch_nr,
                    products.product_name,
                    shore_a_prep.prepared_date
                FROM shore_a_preparation AS shore_a_prep
                JOIN samples
                ON samples.sample_id = shore_a_prep.sample_id
                JOIN products
                ON products.product_id = samples.product_id
                LEFT JOIN shore_a
                ON shore_a.sample_id = samples.sample_id
                WHERE shore_a.sample_id IS NULL
                ORDER BY prepared_date DESC
                """
            )

            return cursor.fetchall()

        finally:
            cursor.close()
            connection.close()