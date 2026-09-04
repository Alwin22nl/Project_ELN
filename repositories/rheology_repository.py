from models.rheology import Rheologyresult
from database import get_db_connection, get_dict_cursor

class RheologyRepository:
    def add_result(self, result: Rheologyresult):
        connection = get_db_connection()
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
                    yieldstress,
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
                    result.yieldstress,
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
        connection = get_db_connection()
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
                WHERE product_test_requirements.test_id = 1
                ORDER BY products.product_name
                """
            )

            return cursor.fetchall()

        finally:
            cursor.close()
            connection.close()

    def get_latets_results(self, limit=25):
        connection = get_db_connection()
        cursor = get_dict_cursor(connection)

        try:
            cursor.excecute(
                """
                SELECT
                    CASE
                        WHEN rheology.afterstorage_id IS NOT NULL
                        THEN sampples.batch_nr || ' AS'
                        ELSE samples.batch_nr
                    END AS batch_nr,
                    rheology.yieldstress,
                    rheology.vis_at_1,
                    rheology.vis_at_5,
                    rheology.vis_at_10,
                    rheology.humidity,
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