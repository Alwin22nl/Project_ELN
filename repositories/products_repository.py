from models.products import Product
from database import get_connection, get_dict_cursor

class ProductsRepository:
    def create_product(self, product, requirements):
        connection = get_connection()
        cursor = get_dict_cursor(connection)

        try:
            cursor.execute(
                """
                INSERT INTO products
                (
                    product_code,
                    product_name
                )
                VALUES
                (%s,%s)
                RETURNING product_id
                """,
                (
                    product.product_code,
                    product.product_name
                )
            )

            product_id = cursor.fetchone()["product_id"]

            for requirement in requirements:
                cursor.execute(
                    """
                    INSERT INTO product_test_requirements
                    (
                        product_id,
                        test_type_id,
                        frequency
                    )
                    VALUES
                    (%s,%s,%s)
                    """,
                    (
                        product_id,
                        requirement["test_type_id"],
                        requirement["frequency"]
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
                    product_code,
                    product_name
                FROM products
                ORDER BY product_code
                """
            )

            return cursor.fetchall()

        finally:
            cursor.close()
            connection.close()

    def get_test_types(self):
        connection = get_connection()
        cursor = get_dict_cursor(connection)

        try:
            cursor.execute(
                """
                SELECT 
                    test_type_id,
                    test_name
                FROM test_types
                ORDER BY test_name
                """
            )

            return cursor.fetchall()

        finally:
            cursor.close()
            connection.close()

