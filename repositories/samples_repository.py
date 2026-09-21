from database import get_connection, get_dict_cursor
from models.samples import Samples

class SampleRepository:
    def batch_exists(self, batch_nr):
        connection = get_connection()
        cursor = get_dict_cursor(connection)

        try:
            cursor.execute(
                """
                SELECT count(*) AS count
                FROM samples
                WHERE batch_nr = %s
                """,
                (batch_nr,)
            )

            return cursor.fetchone()["count"] > 0

        finally: 
            cursor.close()
            connection.close()

    def get_next_sequence(self, product_id):
        connection = get_connection()
        cursor = get_dict_cursor(connection)

        try:
            cursor.execute(
                """
                SELECT 
                    COALESCE(MAX(batch_sequence), 0) +1 AS next_sequence
                FROM samples
                WHERE product_id = %s
                """,
                (product_id,)
            )

            return cursor.fetchone()["next_sequence"]

        finally:
            cursor.close()
            connection.close()

    def add_sample(self, sample: Samples, batch_sequence):
        connection = get_connection()
        cursor = connection.cursor()

        try:
            cursor.execute(
                """
                INSERT INTO samples
                (
                    batch_nr,
                    prod_date,
                    product_id,
                    batch_sequence,
                    after_storage_required,
                    remark
                )
                VALUES
                (%s,%s,%s,%s,%s,%s)
                """,
                (
                    sample.batch_nr,
                    sample.prod_date,
                    sample.product_id,
                    batch_sequence,
                    sample.afterstorage_required,
                    sample.remark
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

    def get_recent_samples(self, limit=25):
        connection = get_connection()
        cursor = get_dict_cursor(connection)

        try:
            cursor.execute(
                """
                SELECT
                    samples.sample_id,
                    samples.batch_nr,
                    samples.prod_date,
                    samples.product_id,
                    products.product_name
                FROM samples
                JOIN products
                ON products.product_id = samples.product_id
                ORDER BY samples.sample_id DESC
                LIMIT %s
                """,
                (limit,)
            )

            return cursor.fetchall()

        finally:
            cursor.close()
            connection.close()

    def get_required_tests(self, product_ids):
        connection = get_connection()
        cursor = get_dict_cursor(connection)

        try:
            cursor.execute(
                """
                SELECT
                    product_id,
                    test_type_id
                FROM product_test_requirements
                WHERE product_id = ANY(%s)
                """,
                (product_ids,)
            )

            return cursor.fetchall()

        finally:
            cursor.close()
            connection.close()

    def get_completed_tests(self, sample_ids):
        connection = get_connection()
        cursor = get_dict_cursor(connection)

        try:
            cursor.execute(
                """
                SELECT 1 AS test_type_id, sample_id
                FROM rheology
                WHERE sample_id = ANY(%s)

                UNION

                SELECT 2 AS test_type_id, sample_id
                FROM curability
                WHERE sample_id = ANY(%s)

                UNION

                SELECT 3 AS test_type_id, sample_id
                FROM shore_a
                WHERE sample_id = ANY(%s)

                UNION

                SELECT 4 AS test_type_id, sample_id
                FROM density
                WHERE sample_id = ANY(%s)

                UNION    

                SELECT 5 AS test_type_id, sample_id
                FROM tensile_strength
                WHERE sample_id = ANY(%s)

                UNION

                SELECT 6 AS test_type_id, sample_id
                FROM adhesion
                WHERE sample_id = ANY(%s)

                UNION

                SELECT 7 AS test_type_id, sample_id
                FROM epdm_adhesion
                WHERE sample_id = ANY(%s)

                UNION

                SELECT 8 AS test_type_id, sample_id
                FROM initial_tack
                WHERE sample_id = ANY(%s)

                UNION 

                SELECT 9 AS test_type_id, sample_id
                FROM skinformation
                WHERE sample_id = ANY(%s)                           
                """,
                (
                    sample_ids,
                    sample_ids,
                    sample_ids,
                    sample_ids,
                    sample_ids,
                    sample_ids,
                    sample_ids,
                    sample_ids,
                    sample_ids,
                )
            )

            return cursor.fetchall()

        finally: 
            cursor.close()
            connection.close()

    def append_remark(self, sample_id, appended_remark):
        connection = get_connection()
        cursor = get_dict_cursor(connection)

        try:
            cursor.execute(
                """
                UPDATE samples
                SET remark = 
                    CASE
                        WHEN remark IS NULL OR remark = ''
                        THEN %s
                        ELSE remark || E'\\n' || %s
                    END
                WHERE sample_id = %s
                """,
                (
                    appended_remark,
                    appended_remark,
                    sample_id,
                )
            )

            connection.commit()

        except Exception:
            connection.rollback()
            raise

        finally: 
            cursor.close()
            connection.close()

    def get_samples_by_product(self, product_id):
        connection = get_connection()
        cursor = get_dict_cursor(connection)

        try:
            cursor.execute(
                """
                SELECT
                    sample_id,
                    batch_nr,
                    prod_date,
                    remark
                FROM samples
                WHERE product_id = %s
                ORDER BY 
                    prod_date DESC NULLS LAST,
                    sample_id DESC
                """,
                (product_id,)
            )

            return cursor.fetchall()

        finally:
            cursor.close()
            connection.close()
    
