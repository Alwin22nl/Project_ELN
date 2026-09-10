from models.curability import CurabilityPrep, CurabilityTest
from database import get_connection, get_dict_cursor

class CurabilityRepository:
    def add_curability_prep(self, result: CurabilityPrep):
        connection = get_connection()
        cursor = connection.cursor()

        try:
            cursor.execute(
                """
                INSERT INTO curability_preparation
                (
                    sample_id,
                    operator_id,
                    afterstorage_id,
                    remark
                )
                VALUES
                (%s,%s,%s,%s)
                """,
                (
                    result.sample_id,
                    result.operator_id,
                    result.afterstorage_id,
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

    def add_results(self, results: list[CurabilityTest]):
        connection = get_connection()
        cursor = connection.cursor()

        try:
            for result in results:
                cursor.execute(
                    """
                    INSERT INTO curability
                    (
                        sample_id,
                        afterstorage_id,
                        operator_id,
                        remark,
                        day_1,
                        temp_day1,
                        rh_day1,
                        day_7,
                        temp_day7,
                        rh_day7
                    )
                    VALUES
                    (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                    """,
                    (
                        result.sample_id,
                        result.afterstorage_id,
                        result.operator_id,
                        result.remark,
                        result.day_1,
                        result.temp_day1,
                        result.rh_day1,
                        result.day_7,
                        result.temp_day7,
                        result.rh_day7,
                    )
                )

            connection.commit()

        except Exception:
            connection.rollback()
            raise

        finally:
            cursor.close()
            connection.close()

    def curability_remove_24h(self, curability_preparation_id):
        connection = get_connection()
        cursor = connection.cursor()

        try:
            cursor.execute(
                """
                UPDATE curability_preparation
                SET removed_24h_at = CURRENT_TIMESTAMP
                WHERE curability_preparation_id = %s
                """,
                (curability_preparation_id,)
            )

            connection.commit()

        except Exception:
            connection.rollback()
            raise

        finally: 
            cursor.close()
            connection.close()

    def curability_remove_7d(self, curability_preparation_id):
        connection = get_connection()
        cursor = connection.cursor()

        try:
            cursor.execute(
                """
                UPDATE curability_preparation
                SET removed_7d_at = CURRENT_TIMESTAMP
                WHERE curability_preparation_id = %s
                """,
                (curability_preparation_id,)
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
                    samples.sample_id
                    NULL::INTEGER AS afterstorage_id,
                    samples.batch_nr AS display_name,
                    products.product_name
                FROM samples
                JOIN porducts
                ON products.product_id = samples.product_id
                JOIN product_test_requiremenst AS ptr
                ON ptr.product_id = products.product_id
                LEFT JOIN curability_preparation AS curability_prep
                ON curability_prep.sample_id = samples.sample_id
                WHERE ptr.test_type_id = 2
                AND curability.prep.sample_id IS NULL
                AND samples.product_id = %s
                AND samples.prod_date <= CURRENT_DATE - 7
                AND
                (
                    samples.batch_sequence = 1
                    OR
                    MOD(
                        samples.batch_sequence,
                        ptr.frequency
                    ) = 0
                )
                UNION ALL
                SELECT
                    samples.sample_id,
                    after_storage.afterstorage_id,
                    samples.batch_nr || ' AS' AS display_name,
                    products.product_name,
                FROM after_storage
                JOIN samples
                ON samples.sample_id = after_storage.sample_id
                JOIN products
                ON products.product_id = samples.product_id
                LEFT JOIN curability_preparation AS curability_prep
                ON curability_prep.afterstorage_id = after_storage.afterstorage_id
                WHERE after_storage.removed_from_oven IS NOT NULL
                AND curability_prep.afterstorage_id IS NULL
                ORDER BY sample_id
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
                    NULL::INTEGER AS afterstorage_id,
                    samples.batch_nr AS display_name
                FROM curability_preparation AS curability_prep
                JOIN samples
                ON samples.sample_id = curability_prep.sample_id
                LEFT JOIN curability
                ON curability.sample_id = samples.sample_id
                WHERE samples.product_id = %s
                AND curability.sample_id IS NULL
                AND curability_prep.removed_24h_at IS NOT NULL
                AND curability.prep.removed_7d_at IS NOT NULL
                UNION ALL
                SELECT
                    samples.sample_id,
                    after_storage.afterstorage_id,
                    samples.batch_nr || ' AS' AS display_name
                FROM after_storage
                JOIN samples
                ON samples.sample_id = after_storage.sample_id
                JOIN curability_preparation AS curability_prep
                ON curability_prep.afterstorage_id = after_storage.afterstorage_id
                LEFT JOIN curability
                ON curability.afterstorage_id = after_storage.afterstorage_id
                WHERE samples.product_id = %s
                AND curability_prep.removed_24h_at IS NOT NULL
                AND curability_prep.removed_7d_at IS NOT NULL
                AND curability.afterstorage_id IS NULL
                ORDER BY product_id, sample_id;
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
                JOIN product_test_requirements AS ptr
                ON ptr.product_id = products.product_id
                WHERE ptr.test_type_id = 2
                ORDER BY products.product_name
                """
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
                    curability_prep.curability_preparation_id,
                    samples.sample_id,
                    curability_prep.afterstorage_id
                    CASE
                        WHEN curability_prep.afterstorage_id IS NOT NULL
                        THEN samples.batch_nr || ' AS'
                        ELSE samples.batch_nr
                        END AS display_name,
                    products.product_name,
                    curability_prep.prepared_date,
                    curability_prep.removed_24h_at,
                    curability_prep.removed_7d_at
                FROM curability_preparation AS curability_prep
                JOIN samples
                ON samples.sample_id = curability_prep.sample_id
                JOIN products
                ON products.product_id = samples.product_id
                LEFT JOIN curability
                ON(
                    curability_prep.after_storage_id IS NULL
                    AND curability.sample_id is samples.sample_id
                )
                OR (
                    curability_prep.afterstorage_id IS NOT NULL
                    AN curability.afterstorage_id = curability_prep.afterstorage_id
                )
                WHERE curability.curability_id IS NULL
                ORDER BY curability_prep.prepared_date DESC
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
                    samples.batch_nr AS display_name
                    curability.day_1,
                    curability.tmp_day1,
                    curability.rh_day1,
                    curability.day_7,
                    curability.temp_day7,
                    curability.rh_day7
                FROM curability
                JOIN samples
                ON samples.sample_id = curability.sample_id
                ORDER BY curability.sample_id DESC
                LIMIT %s
                """,
                (limit,),
            )

            return cursor.fetchall()

        finally:
            cursor.close()
            connection.close()