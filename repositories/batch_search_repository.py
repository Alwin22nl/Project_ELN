from database import get_connection, get_dict_cursor


class BatchSearchRepository:

    def get_batch_group(self, batch_nr):
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
                    products.product_name,
                    samples.remark
                FROM samples
                JOIN products
                ON products.product_id = samples.product_id
                WHERE
                    samples.batch_nr ILIKE %s
                    OR samples.batch_nr ILIKE %s
                ORDER BY
                    samples.prod_date,
                    samples.sample_id
                """,
                (
                    batch_nr,
                    f"{batch_nr} %"
                )
            )

            return cursor.fetchall()

        finally:
            cursor.close()
            connection.close()


    def get_required_tests(self, product_id):
        connection = get_connection()
        cursor = get_dict_cursor(connection)

        try:
            cursor.execute(
                """
                SELECT test_type_id
                FROM product_test_requirements
                WHERE product_id = %s
                ORDER BY test_type_id
                """,
                (product_id,)
            )

            return [
                row["test_type_id"]
                for row in cursor.fetchall()
            ]

        finally:
            cursor.close()
            connection.close()

    def get_rheology(
        self,
        sample_ids,
        afterstorage=False
    ):
        connection = get_connection()
        cursor = get_dict_cursor(connection)

        try:
            if afterstorage:
                afterstorage_condition = """
                    AND afterstorage_id IS NOT NULL
                """
            else:
                afterstorage_condition = """
                    AND afterstorage_id IS NULL
                """

            cursor.execute(
                f"""
                SELECT
                    sample_id,
                    yield_stress,
                    vis_at_1,
                    vis_at_5,
                    vis_at_10,
                    humidity
                FROM rheology
                WHERE sample_id = ANY(%s)
                {afterstorage_condition}
                """,
                (sample_ids,)
            )

            return cursor.fetchall()

        finally:
            cursor.close()
            connection.close()

    def get_initial_tack(self, sample_ids):
        connection = get_connection()
        cursor = get_dict_cursor(connection)

        try:
            cursor.execute(
                """
                SELECT
                    sample_id,
                    initial_tack,
                    humidity
                FROM initial_tack
                WHERE sample_id = ANY(%s)
                """,
                (sample_ids,)
            )

            return cursor.fetchall()

        finally:
            cursor.close()
            connection.close()

    def get_skinformation(
        self,
        sample_ids,
        afterstorage=False
    ):
        connection = get_connection()
        cursor = get_dict_cursor(connection)

        try:
            if afterstorage:
                afterstorage_condition = """
                    AND afterstorage_id IS NOT NULL
                """
            else:
                afterstorage_condition = """
                    AND afterstorage_id IS NULL
                """

            cursor.execute(
                f"""
                SELECT
                    sample_id,
                    tack_free_time,
                    skinformation_time
                FROM skinformation
                WHERE sample_id = ANY(%s)
                {afterstorage_condition}
                """,
                (sample_ids,)
            )

            return cursor.fetchall()

        finally:
            cursor.close()
            connection.close()

    def get_density(self, sample_ids):
        connection = get_connection()
        cursor = get_dict_cursor(connection)

        try:
            cursor.execute(
                """
                SELECT
                    sample_id,
                    density_product
                FROM density
                WHERE sample_id = ANY(%s)
                """,
                (sample_ids,)
            )

            return cursor.fetchall()

        finally:
            cursor.close()
            connection.close()

    def get_shore_a(self, sample_ids):
        connection = get_connection()
        cursor = get_dict_cursor(connection)

        try:
            cursor.execute(
                """
                SELECT
                    sample_id,
                    shore_a_avg,
                    temperature,
                    humidity
                FROM shore_a
                WHERE sample_id = ANY(%s)
                """,
                (sample_ids,)
            )

            return cursor.fetchall()

        finally:
            cursor.close()
            connection.close()

    def get_curability(
        self,
        sample_ids,
        afterstorage=False
    ):
        connection = get_connection()
        cursor = get_dict_cursor(connection)

        try:
            if afterstorage:
                afterstorage_condition = """
                    AND afterstorage_id IS NOT NULL
                """
            else:
                afterstorage_condition = """
                    AND afterstorage_id IS NULL
                """

            cursor.execute(
                f"""
                SELECT
                    sample_id,
                    day_1,
                    day_7
                FROM curability
                WHERE sample_id = ANY(%s)
                {afterstorage_condition}
                """,
                (sample_ids,)
            )

            return cursor.fetchall()

        finally:
            cursor.close()
            connection.close()

    def get_tensile_sample_averages(
        self,
        sample_ids
    ):

        connection = get_connection()
        cursor = get_dict_cursor(connection)

        try:
            cursor.execute(
                """
                SELECT
                    tensile_specimen.sample_id,
                    ROUND(
                        AVG(tensile_specimen.t_50),
                        3
                    ) AS t_50,
                    ROUND(
                        AVG(tensile_specimen.t_100),
                        3
                    ) AS t_100,
                    ROUND(
                        AVG(tensile_specimen.t_max),
                        3
                    ) AS t_max,
                    ROUND(
                        AVG(tensile_specimen.e_max),
                        3
                    ) AS e_max
                FROM tensile_specimen
                WHERE
                    tensile_specimen.sample_id = ANY(%s)
                    AND EXISTS (
                        SELECT 1
                        FROM tensile_strength
                        WHERE
                            tensile_strength.sample_id =
                            tensile_specimen.sample_id
                    )
                GROUP BY
                    tensile_specimen.sample_id
                """,
                (sample_ids,)
            )

            return cursor.fetchall()

        finally:
            cursor.close()
            connection.close()

    def get_adhesion(self, sample_ids):
        connection = get_connection()
        cursor = get_dict_cursor(connection)

        try:
            cursor.execute(
                """
                SELECT
                    sample_id,
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
                FROM adhesion
                WHERE sample_id = ANY(%s)
                ORDER BY sample_id
                """,
                (sample_ids,)
            )

            return cursor.fetchall()

        finally:
            cursor.close()
            connection.close()

    def get_epdm_adhesion(self, sample_ids):
        connection = get_connection()
        cursor = get_dict_cursor(connection)

        try:
            cursor.execute(
                """
                SELECT
                    sample_id,
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
                FROM epdm_adhesion
                WHERE sample_id = ANY(%s)
                ORDER BY sample_id
                """,
                (sample_ids,)
            )

            return cursor.fetchall()

        finally:
            cursor.close()
            connection.close()