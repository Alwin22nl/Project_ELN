from models.rheology import RheologyResult
from database import get_connection, get_dict_cursor

class RheologyRepository:
    def add_result(self, result: RheologyResult):
        connection = get_connection()
        cursor = connection.cursor()

        try:
            cursor.execute(
                """
                INSERT INTO rheology
                (
                    sample_id,
                    afterstorage_id,
                    operator_id,
                    remark,
                    yield_stress,
                    vis_at_1,
                    vis_at_5,
                    vis_at_10,
                    humidity
                )
                VALUES
                (%s,%s,%s,%s,%s,%s,%s,%s,%s)
                """,
                (
                    result.sample_id,
                    result.afterstorage_id,
                    result.operator_id,
                    result.remark,
                    result.yield_stress,
                    result.vis_at_1,
                    result.vis_at_5,
                    result.vis_at_10,
                    result.humidity
                ),
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
                WHERE product_test_requirements.test_type_id = 1
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
                    CASE
                        WHEN rheology.afterstorage_id IS NOT NULL
                        THEN samples.batch_nr || ' AS'
                        ELSE samples.batch_nr
                    END AS batch_nr,
                    rheology.yield_stress,
                    rheology.vis_at_1,
                    rheology.vis_at_5,
                    rheology.vis_at_10,
                    rheology.humidity
                    FROM rheology
                    JOIN samples
                        ON samples.sample_id = rheology.sample_id
                    ORDER BY rheology.rheology_id DESC
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
                    NULL::INTEGER AS afterstorage_id,
                    samples.batch_nr AS display_name
                FROM samples
                LEFT JOIN rheology
                    ON rheology.sample_id = samples.sample_id
                WHERE samples.product_id = %s
                    AND samples.prod_date <= CURRENT_DATE -7
                    AND MOD(
                        samples.batch_sequence,
                        (
                            SELECT frequency
                            FROM product_test_requirements
                            WHERE product_id = samples.product_id
                                AND test_type_id = 1
                        )   
                    ) = 0
                    AND rheology.rheology_id IS NULL
                UNION ALL
                SELECT 
                    samples.sample_id,
                    after_storage.afterstorage_id,
                    samples.batch_nr || ' AS' AS display_name
                FROM after_storage
                JOIN samples
                    ON samples.sample_id = after_storage.sample_id
                LEFT JOIN rheology
                    ON rheology.afterstorage_id = after_storage.afterstorage_id
                WHERE samples.product_id = %s
                    AND after_storage.removed_from_oven IS NOT NULL
                    AND rheology.afterstorage_id IS NULL
                ORDER BY sample_id
                """,
                (product_id, product_id),           
            )

            return cursor.fetchall()

        finally:
            cursor.close()
            connection.close()