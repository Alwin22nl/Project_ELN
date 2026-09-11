from models.tensile import TensileTest, TensileMeasure, TensilePrep
from database import get_connection, get_dict_cursor

class TensileRepository:
    def add_prep_result(self, result: TensilePrep):
        connection = get_connection()
        cursor = connection.cursor()

        try: 
            cursor.execute(
                """
                INSERT INTO tensile_strength_preparation
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

    def add_specimens(self, specimens: list[TensileMeasure]):
        connection = get_connection()
        cursor = connection.cursor()

        try:
                
            for specimen in specimens:
                cursor.execute(
                    """
                    INSERT INTO tensile_specimen
                    (
                        sample_id,
                        specimen_no,

                        width_1,
                        width_2,
                        width_3,
                        width_avg,

                        thickness_1,
                        thickness_2,
                        thickness_3,
                        thickness_avg
                    ) 
                    VALUES
                    (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                    """,
                    (
                        specimen.sample_id,
                        specimen.specimen_no,

                        specimen.width_1,
                        specimen.width_2,
                        specimen.width_3,
                        specimen.calculate_width_avg(),

                        specimen.thickness_1,
                        specimen.thickness_2,
                        specimen.thickness_3,
                        specimen.calculate_thickness_avg(),
                    )
                )

            connection.commit()

        except Exception:
            connection.rollback()
            raise

        finally:
            cursor.close()
            connection.close()

    def complete_test(self, sample_id, operator_id, results: list[TensileTest]):
        connection = get_connection()
        cursor = connection.cursor()

        try:
            for result in results:

                cursor.execute(
                    """
                    UPDATE tensile_specimen
                    SET
                        t_max = %s,
                        e_max = %s,
                        t_50 = %s,
                        t_100 = %s,
                        remark = %s,
                    WHERE specimen_id = %s
                    """,
                    (
                        result.t_max,
                        result.e_max,
                        result.t_50,
                        result.t_100,
                        result.remark,
                        result.specimen_id,
                    )
                )

            cursor.execute(
                """
                INSERT INTO tensile_strength
                (
                    sample_id,
                    operator_id,
                    remark
                )
                VALUES
                (%s,%s,%s)
                """,
                (
                    sample_id,
                    operator_id,
                    "",
                )
            )

            connection.commit()

        except Exception:
            connection.rollback()
            raise

        finally:
            cursor.close()
            connection.close()

    def get_samples_for_prep(self):
        connection = get_connection()
        cursor = get_dict_cursor(connection)

        try:
            cursor.execute(
                """
                SELECT
                    samples.sample_id,
                    samples.batch_nr,
                    products.product_name
                FROM samples
                JOIN products
                ON products.product_id = samples.product_id
                JOIN product_test_requirements
                ON product_test_requirements.product_id =
                products.product_id
                LEFT JOIN tensile_strength_preparation
                ON tensile_strength_preparation.sample_id =
                samples.sample_id
                WHERE
                    product_test_requirements.test_type_id = 5
                AND tensile_strength_preparation.sample_id IS NULL
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
                """
            )

            return cursor.fetchall()

        finally:
            cursor.close()
            connection.close()

    def get_samples_for_measurement(self):
        connection = get_connection()
        cursor = get_dict_cursor(connection)

        try:
            cursor.execute(
                """
                SELECT
                    samples.sample_id,
                    samples.batch_nr,
                    products.product_name
                FROM tensile_strength_preparation
                JOIN samples
                ON samples.sample_id = tensile_strength_preparation.sample_id
                JOIN products
                ON products.product_id = samples.product_id
                LEFT JOIN tensile_specimen
                ON tensile_specimen.sample_id = samples.sample_id
                WHERE tensile_specimen.sample_id IS NULL
                AND tensile_strength_preparation.prepared_date::date
                <= CURRENT_DATE - INTERVAL '7 days'
                ORDER BY samples.product_id, samples.sample_id;                
                """
            )

            return cursor.fetchall()

        finally:
            cursor.close()
            connection.close()

    def get_samples_for_test(self):
        connection = get_connection()
        cursor = get_dict_cursor(connection)

        try:
            cursor.execute(
                """
                SELECT DISTINCT
                    samples.sample_id,
                    samples.batch_nr,
                    products.product_name
                FROM tensile_specimen
                JOIN samples
                ON samples.sample_id =
                tensile_specimen.sample_id
                JOIN products
                ON products.product_id =
                samples.product_id
                WHERE tensile_specimen.t_max IS NULL
                ORDER BY samples.sample_id;
                """
            )

            return cursor.fetchall()

        finally:
            cursor.close()
            connection.close()

    def get_tensile_specimens(self, sample_id):
        connection = get_connection()
        cursor = get_dict_cursor(connection)

        try:
            cursor.execute(
                """
                SELECT
                    specimen_id,
                    specimen_no,
                    width_avg,
                    thickness_avg
                FROM tensile_specimen
                WHERE sample_id = %s
                ORDER BY specimen_no
                """,
                (sample_id,)
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
                    samples.sample_id,
                    samples.batch_nr,
                    products.product_name,
                    tensile_strength_preparation.prepared_date,
                    EXISTS
                    (
                        SELECT 1
                        FROM tensile_specimen
                        WHERE tensile_specimen.sample_id = samples.sample_id
                    ) AS measured
                FROM tensile_strength_preparation
                JOIN samples
                ON samples.sample_id = tensile_strength_preparation.sample_id
                JOIN products
                ON products.product_id = samples.product_id
                LEFT JOIN tensile_strength
                ON tensile_strength.sample_id = samples.sample_id
                WHERE tensile_strength.sample_id IS NULL
                ORDER BY tensile_strength_preparation.prepared_date DESC;
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
                    ROUND(AVG(tensile_specimen.t_max),2)
                    AS t_max,
                    ROUND(AVG(tensile_specimen.e_max),2)
                    AS e_max,
                    ROUND(AVG(tensile_specimen.t_50),2)
                    AS t_50,
                    ROUND(AVG(tensile_specimen.t_100),2)
                    AS t_100
                FROM tensile_specimen
                JOIN samples
                ON samples.sample_id =
                tensile_specimen.sample_id
                WHERE tensile_specimen.t_max IS NOT NULL
                GROUP BY samples.batch_nr
                ORDER BY MAX(samples.sample_id) DESC
                LIMIT %s
                """,
                (limit,)
            )

            return cursor.fetchall()

        finally: 
            cursor.close()
            connection.close()