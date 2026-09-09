from models.epdm_adhesion import EpdmAdhesionPrep, EpdmAdhesionTest
from database import get_connection, get_dict_cursor

class EpdmAdhesionRepository:
    def add_epdm_adhesion_prep(self, result: EpdmAdhesionPrep):
        connection = get_connection()
        cursor = connection.cursor()

        try:
            cursor.execute(
                """
                INSERT INTO epdm_adhesion_preparation
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

    def submit_test_results(self, result: EpdmAdhesionTest):
        connection = get_connection()
        cursor = connection.cursor()

        try:
            cursor.execute(
                """
                INSERT INTO epdm_adhesion
                (
                    sample_id,
                    operator_id,
                    remark,
                    europees,
                    trc,
                    carlisle,
                    rubber,
                    copper,
                    wood,
                    aluminium,
                    aluminium_anod,
                    lead,
                    rvs,
                    concrete,
                    glass,
                    pvc,
                    pmma,
                    pc
                )
                VALUES
                (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                """,
                (
                    result.sample_id,
                    result.operator_id,
                    result.remark,
                    result.europees,
                    result.trc,
                    result.carlisle,
                    result.rubber,
                    result.copper,
                    result.wood,
                    result.aluminium,
                    result.aluminium_anod,
                    result.lead,
                    result.rvs,
                    result.concrete,
                    result.glass,
                    result.pvc,
                    result.pmma,
                    result.pc,
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
                JOIN product_test_requirements AS ptr
                ON ptr.product_id = products.product_id
                LEFT JOIN epdm_adhesion_preparation AS epdm_prep
                ON epdm_prep.sample_id = samples.sample_id
                WHERE ptr.test_type_id = 7
                AND samples.product_id = %s
                AND epdm_prep IS NULL
                AND samples.prod_date <= CURRENT_DATE -7
                AND
                (
                    samples.batch_sequence = 1
                    OR
                    MOD(
                        samples.batch_sequence,
                        ptr.frequency
                    ) = 0
                )
                ORDER BY samples.batch_sequence
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
                FROM sampels
                JOIN epdm_adhesion_preparation AS epdm_prep
                ON epdm_prep.sample_id = samples.sample_id
                LEFT JOIN epdm_adhesion
                ON epdm_adhesion.sample_id = samples.sample_id
                WHERE samples.product_id = %s
                AND epdm_adhesion.sample_id IS NULL
                AND epdm_prep.prepared_date:: <= CURRENT_DATE - INTERVAL '7 days'
                ORDER BY samples.sample_id
                """
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
                WHERE ptr.test_type_id = 7
                ORDER BY products.product_name
                """
            )

            return cursor.fetchall

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
                    epdm_adhesion.europees,
                    epdm_adhesion.trc,
                    epdm_adhesion.carlisle
                FROM epdm_adhesion
                JOIN samples 
                ON samples.sample_id = epdm_adhesion.sample_id
                ORDER BY epdm_adhesion.epdm_adhesion_id DESC
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
                    epdm_prep.prepared_date
                FROM epdm_adhesion_preparation AS epdm_prep
                JOIN samples 
                ON samples.sample_id = epdm_prep.sample_id
                JOIN products
                ON products.product_id = samples.product_id
                LEFT JOIN epdm_adhesion
                ON epdm_adhesion.sample_id = samples.sample_id
                WHERE epdm_adhesion.sample_id IS NULL
                ORDER BY prepared_date DESC
                """
            )

            return cursor.fetchall()

        finally:
            cursor.close()
            connection.close()