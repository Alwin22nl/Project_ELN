from models.density import DensityResult
from database import get_connection, get_dict_cursor

class DensityRepository:
    def add_result(self, result: DensityResult, density_product: float):
        connection = get_connection()
        cursor = connection.cursor()

        try:
            cursor.execute(
                """
                INSERT INTO density
                (
                    sample_id,
                    operator_id,
                    remark,
                    vessel_empty,
                    vessel_full,
                    vessel_volume
                    density_product
                )
                VALUES (%s,%s,%s,%s,%s,%s,%s)
                """,
                (
                    result.sample_id,
                    result.operator_id,
                    result.remark,
                    result.vessel_empty,
                    result.vessel_full,
                    result.vessel_volume,
                    density_product,
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
                WHERE product_test_reuirements.test_type_id = 4
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
                    density.density_id
                    samples.batch_nr,
                    density.vessel_empty,
                    density.vessel_full,
                    density.vessel_volume,
                    density.density_product,
                    density.remark
                FROM density
                JOIN samples
                ON samples.sample_id = density.sample_id
                ORDER BY density.density_id DESC
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
                LEFT JOIN density
                ON density.sample_id = samples.sample_id
                WHERE samples.product_id = %s
                AND samples.prod_date <= CURRENT_DATE -7
                AND (
                    samples.batch_sequence = 1
                    OR MOD(
                        SELECT frequency
                        FROM product_test_requirements
                        WHERE product_id = samples.product_id
                        AND test_type_id = 4
                    )
                ) = 0
                AND density.sample_id IS NULL
                ORDER BY samples.sample_id
                """,
                (product_id,),
            )

            return cursor.fetchall()

        finally:
            cursor.close()
            connection.close()
                    