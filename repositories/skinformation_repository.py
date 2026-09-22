from database import get_connection, get_dict_cursor

class SkinformationRepository:
    def add_results(self, results):
        connection = get_connection()
        cursor = connection.cursor()

        try:
            for result in results:
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

    def get_available_samples(self):
        connection = get_connection()
        cursor = get_dict_cursor(connection)

        try:
            cursor.execute(
                """
                SELECT  
                    samples.sample_id,
                    NULL::INTEGER AS afterstorage_id,
                    samples.batch_nr AS display_name,
                    products.product_name
                FROM samples
                JOIN products
                    ON products.product_id = samples.product_id
                JOIN product_test_requirements
                    ON product_test_requirements.product_id = products.product_id
                LEFT JOIN skinformation
                    ON skinformation.sample_id = samples.sample_id
                WHERE samples.prod_date <= CURRENT_DATE -7
                    AND skinformation.sample_id IS NULL
                    AND product_test_requirements.test_type_id = 9
                    AND MOD(
                        samples.batch_sequence,
                        product_test_requirements.frequency     
                    ) = 0
                UNION ALL
                SELECT 
                    samples.sample_id,
                    after_storage.afterstorage_id,
                    samples.batch_nr || ' AS' AS display_name,
                    products.product_name
                FROM after_storage
                JOIN samples
                    ON samples.sample_id = after_storage.sample_id
                LEFT JOIN skinformation
                    ON skinformation.afterstorage_id = after_storage.afterstorage_id
                JOIN products
                    ON products.product_id = samples.product_id
                WHERE after_storage.removed_from_oven IS NOT NULL
                    AND skinformation.afterstorage_id IS NULL
                ORDER BY sample_id
                """    
            )

            return cursor.fetchall()

        finally:
            cursor.close()
            connection.close()