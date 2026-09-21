from database import get_dict_cursor, get_connection

class DashboardRepository:
    def get_dashboard_data(self):
        connection = get_connection
        cursor = get_dict_cursor(connection)

        try:
            return{
                "curability_schedule": self.get_curability_schedule(cursor),
                "after_storage_schedule": self.get_after_storage_schedule(cursor),
                "rheology": self.get_reology_tasks(cursor),
                "skinformation": self.get_skinformation_tasks(cursor),
                "initial_tack": self.get_initial_tack_tasks(cursor),
                "tensile": self.get_tensile_tasks(cursor),
                "shore_a": self.get_shore_a_tasks(cursor),
                "adhesion": self.get_adhesion_tasks(cursor),
                "epdm_adhesion": self.get_epdm_adhesion_tasks(cursor),
                "curability": self.get_curability_tasks(cursor),
                "density": self.get_density_tasks(cursor),
            }

        finally:
            cursor.close()
            connection.close()

    def get_curability_schedule(self, cursor):
        cursor.execute(
            """
            SELECT *
            FROM (
                SELECT
                    samples.sample_id,
                    CASE
                        WHEN curability_preparation.afterstorage_id IS NOT NULL
                            THEN samples.batch_nr || ' AS'
                        ELSE samples.batch_nr
                    END AS batch_nr,
                    products.product_name,
                    samples.prod_date,
                    CASE
                        WHEN curability_preparation.removed_24h_at IS NULL
                            THEN '24h sample Uithalen'
                        WHEN curability_preparation.removed_7d_at IS NULL
                            THEN '7d sample Uithalen'
                    END AS action,
                    CASE
                        WHEN curability_preparation.removed_24h_at IS NULL
                            THEN curability_preparation.prepared_date + INTERVAL '1 day'
                        WHEN curability_preparation.removed_7d_at IS NULL
                            THEN curability_preparation.prepared_date + INTERVAL '7 days'
                    END AS due_time
                FROM samples
                JOIN products
                ON products.product_id = samples.product_id
                LEFT JOIN curability_preparation
                ON curability_preparation.sample_id = samples.sample_id
                WHERE
                    samples.prod_date <= CURRENT_DATE - INTERVAL '7 days'
            ) curability_schedule
            WHERE
                due_time::date = CURRENT_DATE
            ORDER BY due_time;
            """
        )

        return cursor.fetchall()

    def get_after_storage_schedule(self, cursor):
        cursor.execute(
            """
            SELECT *
            FROM (
                SELECT
                    samples.sample_id,
                    samples.batch_nr,
                    products.product_name,
                    NULL AS afterstorage_id,
                    samples.prod_date + INTERVAL '7 days'
                        AS due_date,
                    'Place in oven' AS action
                FROM samples
                JOIN products
                ON products.product_id = samples.product_id
                LEFT JOIN after_storage a
                ON a.sample_id = samples.sample_id
                WHERE
                    samples.after_storage_required = TRUE
                    AND a.afterstorage_id IS NULL
                    AND samples.prod_date + INTERVAL '7 days' <= NOW()
                UNION ALL
                SELECT
                    samples.sample_id,
                    samples.batch_nr,
                    products.product_name,
                    a.afterstorage_id,
                    a.placed_in_oven_at + INTERVAL '28 days'
                        AS due_date,
                    'Remove from oven' AS action
                FROM after_storage a
                JOIN samples
                ON samples.sample_id = a.sample_id
                JOIN products
                ON products.product_id = samples.product_id
                WHERE
                    a.placed_in_oven_at IS NOT NULL
                    AND a.removed_from_oven IS NULL
                    AND a.placed_in_oven_at::date + INTERVAL '28 days'
                        <= NOW()
            ) AS after_storage_schedule
            ORDER BY due_date;
            """
        )

        return cursor.fetchall()

    def get_rheology_tasks(self, cursor):
        cursor.execute(
            """
            SELECT
                samples.sample_id,
                samples.batch_nr,
                samples.prod_date,
                products.product_name,
                NULL::integer AS afterstorage_id
            FROM samples
            JOIN products
            ON products.product_id = samples.product_id
            LEFT JOIN rheology
            ON rheology.sample_id = samples.sample_id
            WHERE
                samples.prod_date <= CURRENT_DATE - INTERVAL '7 DAY'
                AND MOD(
                    samples.batch_sequence,
                    (
                        SELECT frequency
                        FROM product_test_requirements
                        WHERE product_id = samples.product_id
                        AND test_type_id = 1
                    )
                )=0
                AND rheology.sample_id IS NULL
            UNION ALL
            SELECT
                samples.sample_id,
                samples.batch_nr || ' AS' AS batch_nr,
                samples.prod_date,
                products.product_name,
                after_storage.afterstorage_id
            FROM after_storage
            JOIN samples
            ON samples.sample_id = after_storage.sample_id
            JOIN products
            ON products.product_id = samples.product_id
            LEFT JOIN rheology
            ON rheology.afterstorage_id = after_storage.afterstorage_id
            WHERE
            after_storage.removed_from_oven IS NOT NULL
            AND rheology.afterstorage_id IS NULL
            ORDER BY 
                prod_date,
                sample_id
            LIMIT 25;
            """
        )

        return cursor.fetchall()

    def get_skinformation_tasks(self, cursor):
        cursor.execute(
            """
            SELECT
                samples.sample_id,
                samples.batch_nr,
                samples.prod_date,
                products.product_name,
                NULL::integer AS afterstorage_id
            FROM samples
            JOIN products
            ON products.product_id = samples.product_id
            LEFT JOIN skinformation
            ON skinformation.sample_id = samples.sample_id
            WHERE
                samples.prod_date <= CURRENT_DATE - INTERVAL '7 DAY'
                AND MOD(
                    samples.batch_sequence,
                    (
                        SELECT frequency
                        FROM product_test_requirements
                        WHERE product_id = samples.product_id
                        AND test_type_id = 9
                    )
                )=0
                AND skinformation.sample_id IS NULL
            UNION ALL
            SELECT
                samples.sample_id,
                samples.batch_nr || ' AS' AS batch_nr,
                samples.prod_date,
                products.product_name,
                after_storage.afterstorage_id
            FROM after_storage
            JOIN samples
            ON samples.sample_id = after_storage.sample_id
            JOIN products
            ON products.product_id = samples.product_id
            LEFT JOIN skinformation
            ON skinformation.afterstorage_id = after_storage.afterstorage_id
            WHERE
            after_storage.removed_from_oven IS NOT NULL
            AND skinformation.afterstorage_id IS NULL
            ORDER BY 
                prod_date,
                sample_id
            LIMIT 25;
            """
        )

        return cursor.fetchall()

    def get_initial_tack_tasks(self, cursor):
        cursor.execute(
            """
            SELECT
                samples.sample_id,
                samples.batch_nr,
                samples.prod_date,
                products.product_name
            FROM samples
            JOIN products
            ON products.product_id = samples.product_id
            LEFT JOIN initial_tack
            ON initial_tack.sample_id = samples.sample_id
            WHERE
            samples.prod_date <= CURRENT_DATE - INTERVAL '7 DAY'
            AND MOD(
                samples.batch_sequence,
                (
                    SELECT frequency
                    FROM product_test_requirements
                    WHERE product_id = samples.product_id
                    AND test_type_id = 8
                )
            )=0
            AND initial_tack.sample_id IS NULL
            ORDER BY samples.prod_date, samples.sample_id;
            """
        )

        return cursor.fetchall()

    def get_tensile_tasks(self, cursor):
        cursor.execute(
            """
            SELECT *
            FROM (
                SELECT
                    samples.sample_id,
                    samples.batch_nr,
                    samples.prod_date,
                    products.product_name,
                    CASE
                        WHEN tensile_prep.sample_id IS NULL
                        AND samples.prod_date <= CURRENT_date - INTERVAL '7 days'
                            THEN 'Inzetten'
                        WHEN tensile_prep.sample_id IS NOT NULL
                            AND tensile_prep.prepared_date::date <= CURRENT_DATE - INTERVAL '7 days'
                            AND NOT EXISTS (
                            SELECT 1
                            FROM tensile_specimen ts
                            WHERE ts.sample_id = samples.sample_id
                            )
                            THEN 'Opmeten'
                        WHEN tensile_prep.sample_id IS NOT NULL
                            AND EXISTS (
                            SELECT 1
                            FROM tensile_specimen ts
                            WHERE ts.sample_id = samples.sample_id
                            )
                            AND tensile_strength.sample_id IS NULL
                            THEN 'Testen'
                        ELSE NULL
                    END AS action
                FROM samples
                JOIN products
                ON products.product_id = samples.product_id
                LEFT JOIN tensile_strength_preparation AS tensile_prep
                ON tensile_prep.sample_id = samples.sample_id
                LEFT JOIN tensile_strength 
                ON tensile_strength.sample_id = samples.sample_id
                WHERE
                    samples.prod_date <= CURRENT_DATE - INTERVAL '7 days'
                    AND (
                        samples.batch_sequence = 1
                        OR MOD(
                            samples.batch_sequence,
                            (
                                SELECT frequency
                                FROM product_test_requirements
                                WHERE product_id = samples.product_id
                                AND test_type_id = 5
                            )
                        ) = 0
                    )
            ) tensile_tasks
            WHERE action IS NOT NULL        
            ORDER BY prod_date, sample_id
            LIMIT 25;
            """
        )

        return cursor.fetchall()

    def get_shore_a_tasks(self, cursor):
        cursor.execute(
            """
            SELECT *
            FROM (
                SELECT
                    samples.sample_id,
                    samples.batch_nr,
                    samples.prod_date,
                    products.product_name,
                    CASE
                        WHEN shore_a_prep.sample_id IS NULL
                        AND samples.prod_date <= CURRENT_date - INTERVAL '7 days'
                            THEN 'Inzetten'
                        WHEN shore_a_prep.sample_id IS NOT NULL    
                        AND shore_a_prep.prepared_date::date <= CURRENT_DATE - INTERVAL '7 days'
                        AND shore_a.sample_id IS NULL
                            THEN 'Testen'
                        ELSE NULL
                    END AS action
                FROM samples
                JOIN products
                ON products.product_id = samples.product_id
                LEFT JOIN shore_a_preparation AS shore_a_prep
                ON shore_a_prep.sample_id = samples.sample_id
                LEFT JOIN shore_a 
                ON shore_a.sample_id = samples.sample_id
                WHERE
                    samples.prod_date <= CURRENT_DATE - INTERVAL '7 days'
                    AND MOD(
                        samples.batch_sequence,
                        (
                            SELECT frequency
                            FROM product_test_requirements
                            WHERE product_id = samples.product_id
                            AND test_type_id = 3
                        )
                    ) = 0
            ) shore_a_tasks
            WHERE action IS NOT NULL
            ORDER BY prod_date, sample_id
            LIMIT 25;
            """
        )

        return cursor.fetchall()

    def get_adhesion_tasks(self, cursor):
        cursor.execute(
            """
            SELECT *
            FROM (
                SELECT
                    samples.sample_id,
                    samples.batch_nr,
                    samples.prod_date,
                    products.product_name,
                    CASE
                        WHEN adhesion_prep.sample_id IS NULL
                        AND samples.prod_date <= CURRENT_date - INTERVAL '7 days'
                            THEN 'Inzetten'
                        WHEN adhesion_prep.sample_id IS NOT NULL
                            AND adhesion_prep.prepared_date::date <= CURRENT_DATE - INTERVAL '7 days'
                            AND adhesion.sample_id IS NULL
                            THEN 'Testen'
                        ELSE NULL
                    END AS action
                FROM samples
                JOIN products
                ON products.product_id = samples.product_id
                LEFT JOIN adhesion_preparation AS adhesion_prep
                ON adhesion_prep.sample_id = samples.sample_id
                LEFT JOIN adhesion 
                ON adhesion.sample_id = samples.sample_id
                WHERE
                    samples.prod_date <= CURRENT_DATE - INTERVAL '7 days'
                    AND EXISTS (
                        SELECT 1
                        FROM product_test_requirements ptr
                        WHERE ptr.product_id = samples.product_id
                        AND ptr.test_type_id = 6
                    )
                    AND(
                        samples.batch_sequence = 1
                        OR MOD(
                            samples.batch_sequence,
                            (
                                SELECT frequency
                                FROM product_test_requirements
                                WHERE product_id = samples.product_id
                                AND test_type_id = 6
                            )
                        ) = 0  
                    )             
            ) adhesion_tasks
            WHERE action IS NOT NULL
            ORDER BY prod_date, sample_id
            LIMIT 25;
            """
        )

        return cursor.fetchall()

    def get_epdm_adhesion_tasks(self, cursor):
        cursor.execute(
            """
            SELECT *
            FROM (
                SELECT
                    samples.sample_id,
                    samples.batch_nr,
                    samples.prod_date,
                    products.product_name,
                    CASE
                        WHEN epdm_adhesion_prep.sample_id IS NULL
                        AND samples.prod_date <= CURRENT_date - INTERVAL '7 days'
                            THEN 'Inzetten'
                        WHEN epdm_adhesion_prep.prepared_date::date <= CURRENT_DATE - INTERVAL '7 days'
                        AND epdm_adhesion_prep.sample_id IS NOT NULL
                        AND epdm_adhesion.sample_id IS NULL
                            THEN 'Testen'
                        ELSE NULL
                    END AS action
                FROM samples
                JOIN products
                ON products.product_id = samples.product_id
                LEFT JOIN epdm_adhesion_preparation AS epdm_adhesion_prep
                ON epdm_adhesion_prep.sample_id = samples.sample_id
                LEFT JOIN epdm_adhesion 
                ON epdm_adhesion.sample_id = samples.sample_id
                WHERE
                    samples.prod_date <= CURRENT_DATE - INTERVAL '7 days'
                    AND EXISTS (
                        SELECT 1
                        FROM product_test_requirements ptr
                        WHERE ptr.product_id = samples.product_id
                        AND ptr.test_type_id = 7
                    )

                    AND(
                        samples.batch_sequence = 1
                        OR MOD(
                            samples.batch_sequence,
                            (
                                SELECT frequency
                                FROM product_test_requirements
                                WHERE product_id = samples.product_id
                                AND test_type_id = 7
                            )
                        ) = 0  
                    )             
            ) epdm_adhesion_tasks
            WHERE action IS NOT NULL
            ORDER BY prod_date, sample_id
            LIMIT 25;
            """
        )

        return cursor.fetchall()

    def get_curability_tasks(self, cursor):
        cursor.execute(
            """
            SELECT * 
            FROM 
            (
                SELECT
                    samples.sample_id,
                    samples.batch_nr,
                    samples.prod_date,
                    products.product_name,
                    NULL::INTEGER AS afterstorage_id,
                    CASE
                        WHEN curability_preparation.prepared_date IS NULL
                            THEN 'Inzetten'
                        WHEN curability_preparation.removed_24h_at IS NOT NULL
                        AND curability_preparation.removed_7d_at IS NOT NULL
                        AND (
                            curability.day_1 IS NULL
                            OR curability.day_7 IS NULL
                        )
                            THEN 'Opmeten'
                        ELSE NULL
                    END AS action
                FROM samples
                JOIN products
                ON products.product_id = samples.product_id
                LEFT JOIN curability_preparation
                ON curability_preparation.sample_id = samples.sample_id
                LEFT JOIN curability
                ON curability.sample_id = samples.sample_id
                WHERE
                    samples.prod_date <= CURRENT_DATE - INTERVAL '7 days'
                    AND EXISTS (
                        SELECT 1
                        FROM product_test_requirements ptr
                        WHERE ptr.product_id = samples.product_id
                        AND ptr.test_type_id = 2
                    )
            ) curability_measure_tasks
            WHERE action IS NOT NULL
            UNION ALL
            SELECT *
            FROM
                (
                SELECT
                    samples.sample_id,
                    samples.batch_nr || ' AS' AS batch_nr,
                    samples.prod_date,
                    products.product_name,
                    after_storage.afterstorage_id,
                        CASE
                            WHEN curability_prep.afterstorage_id IS NULL
                                THEN 'Inzetten'
                            WHEN curability_prep.removed_24h_at IS NOT NULL
                            AND curability_prep.removed_7d_at IS NOT NULL
                            AND (
                                curability.day_1 IS NULL
                                OR curability.day_7 IS NULL
                            )
                                THEN 'Opmeten'
                            ELSE NULL
                        END AS action
                FROM after_storage
                JOIN samples
                ON samples.sample_id = after_storage.sample_id
                LEFT JOIN curability
                ON curability.afterstorage_id = after_storage.afterstorage_id
                JOIN products
                ON products.product_id = samples.product_id
                LEFT JOIN curability_preparation AS curability_prep
                ON curability_prep.afterstorage_id = after_storage.afterstorage_id
                WHERE
                after_storage.removed_from_oven IS NOT NULL
                ) curability_as_tasks 
                WHERE action IS NOT NULL
            ORDER BY prod_date, sample_id
            LIMIT 25;
            """
        )

        return cursor.fetchall()

    def get_density_tasks(self, cursor):
        cursor.execute(
            """
            SELECT
                samples.sample_id,
                samples.batch_nr,
                samples.prod_date,
                products.product_name
            FROM samples
            JOIN products
            ON products.product_id = samples.product_id
            LEFT JOIN density
            ON density.sample_id = samples.sample_id
            WHERE
            samples.prod_date <= CURRENT_DATE - INTERVAL '7 days'
                    AND EXISTS (
                        SELECT 1
                        FROM product_test_requirements ptr
                        WHERE ptr.product_id = samples.product_id
                        AND ptr.test_type_id = 4
                    )
                    AND(
                        samples.batch_sequence = 1
                        OR MOD(
                            samples.batch_sequence,
                            (
                                SELECT frequency
                                FROM product_test_requirements
                                WHERE product_id = samples.product_id
                                AND test_type_id = 4
                            )
                        ) = 0  
                    )
            AND density.sample_id IS NULL
            ORDER BY samples.prod_date, samples.sample_id
            LIMIT 25;
            """
        )

        return cursor.fetchall()

    def place_afterstorage(self, sample_id, oven_location):
        connection = get_connection()
        cursor = connection.cursor()

        try:
            cursor.execute(
                """
                INSERT INTO after_storage
                    (
                        sample_id,
                        placed_in_oven_at,
                        oven_location
                    )
                VALUES
                    (
                        %s,
                        NOW(),
                        %s
                    )
                """,
                (
                    sample_id,
                    oven_location
                )
            )

            connection.commit()

        except Exception:
            connection.rollback()
            raise

        finally:
            cursor.close()
            connection.close()

    def remove_afterstorage(self, afterstorage_id):
        connection = get_connection()
        cursor = connection.cursor()

        try:
            cursor.execute(
            """
            UPDATE after_storage
            SET removed_from_oven = NOW()
            WHERE afterstorage_id = %s
            """,
            (afterstorage_id,)
            )

            connection.commit()

        except Exception:
            connection.rollback()
            raise

        finally:
            cursor.close()
            connection.close()

        