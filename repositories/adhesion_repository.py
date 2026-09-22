from models.adhesion import AdhesionPrep, AdhesionTest
from database import get_connection, get_dict_cursor

class AdhesionRepository:
    def add_adhesion_prep(self, result: AdhesionPrep):
        connection = get_connection()
        cursor = connection.cursor()

        try:
            cursor.execute(
                """
                INSERT INTO adhesion_preparation
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

    def submit_test_results(self, result: AdhesionTest):
        connection = get_connection()
        cursor = connection.cursor()

        try:
            cursor.execute(
                """
                INSERT INTO adhesion
                (
                    sample_id,
                    operator_id,
                    remark,
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
                (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                """,
                (
                    result.sample_id,
                    result.operator_id,
                    result.remark,
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
                JOIN product_test_requirements
                ON product_test_requirements.product_id = products.product_id
                LEFT JOIN adhesion_preparation AS adhesion_prep
                ON adhesion_prep.sample_id = samples.sample_id
                WHERE product_test_requirements.test_type_id = 6
                AND samples.product_id = %s
                AND adhesion_prep.sample_id IS NULL
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
                FROM adhesion_preparation AS adhesion_prep
                JOIN samples
                ON samples.sample_id = adhesion_prep.sample_id
                LEFT JOIN adhesion
                ON adhesion.sample_id = samples.sample_id
                WHERE samples.product_id = %s
                AND adhesion.sample_id IS NULL
                AND adhesion_prep.prepared_date::date <= CURRENT_DATE - INTERVAL '7 days'
                ORDER BY samples.sample_id
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
                WHERE product_test_requirements.test_type_id = 6
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
                    adhesion.rubber,
                    adhesion.copper,
                    adhesion.wood,
                    adhesion.aluminium,
                    adhesion.aluminium_anod,
                    adhesion.lead,
                    adhesion.rvs,
                    adhesion.concrete,
                    adhesion.glass,
                    adhesion.pvc,
                    adhesion.pmma,
                    adhesion.pc
                FROM adhesion
                JOIN samples
                ON samples.sample_id = adhesion.sample_id
                ORDER BY adhesion.adhesion_id DESC
                lIMIT %s
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
                    adhesion_prep.prepared_date
                FROM adhesion_preparation AS adhesion_prep
                JOIN samples
                ON samples.sample_id = adhesion_prep.sample_id
                JOIN products
                ON products.product_id = samples.product_id
                LEFT JOIN adhesion
                ON adhesion.sample_id = samples.sample_id
                WHERE adhesion.sample_id IS NULL
                ORDER BY prepared_date DESC
                """
            )

            return cursor.fetchall()

        finally:
            cursor.close()
            connection.close()