from database import get_dict_cursor, get_connection

class OverviewRepository:
    def get_products(self):
        connection = get_connection()
        cursor = get_dict_cursor(connection)

        try:
            cursor.execute(
                """
                SELECT
                    product_id,
                    product_name
                FROM products
                ORDER BY product_name
                """
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

    def get_results(
            self,
            product_id,
            batch_nr=None,
            date_from=None,
            date_to=None
    ):
        connection = get_connection()
        cursor = get_dict_cursor(connection)

        try:
            query = """
                SELECT
                    samples.sample_id,
                    samples.batch_nr,
                    samples.prod_date,
                    rheology_normal.yield_stress AS yield_stress,
                    rheology_normal.vis_at_10 AS vis_at_10,
                    rheology_as.yield_stress AS yield_stress_as,
                    rheology_as.vis_at_10 AS vis_at_10_as,
                    ROUND(initial_tack.initial_tack, 2) AS initial_tack,
                    skinformation_normal.tack_free_time AS tack_free_time,
                    skinformation_normal.skinformation_time AS skinformation_time,
                    skinformation_as.tack_free_time AS tack_free_time_as,
                    skinformation_as.skinformation_time AS skinformation_time_as,
                    curability_normal.day_1 AS day_1,
                    curability_normal.day_7 AS day_7,
                    curability_as.day_1 AS day_1_as,
                    curability_as.day_7 AS day_7_as,
                    shore_a.shore_a_avg,
                    ROUND(density.density_product, 2) AS density_product,
                    ROUND(
                        AVG(tensile_specimen.t_max)
                        FILTER (
                            WHERE tensile_specimen.remark IS NULL
                            OR TRIM(tensile_specimen.remark) = ''
                        ),
                        3
                    ) AS t_max,
                    ROUND(
                        AVG(tensile_specimen.e_max)
                        FILTER (
                            WHERE tensile_specimen.remark IS NULL
                            OR TRIM(tensile_specimen.remark) = ''
                        ),
                        3
                    ) AS e_max,
                    CASE
                        WHEN adhesion.sample_id IS NULL
                        THEN ''
                        ELSE '✓'
                    END AS adhesion,
                    CASE
                        WHEN epdm_adhesion.sample_id IS NULL
                        THEN ''
                        ELSE '✓'
                    END AS epdm_adhesion
                FROM samples
                LEFT JOIN after_storage
                    ON after_storage.sample_id = samples.sample_id
                LEFT JOIN rheology AS rheology_normal
                    ON rheology_normal.sample_id = samples.sample_id
                    AND rheology_normal.afterstorage_id IS NULL
                LEFT JOIN rheology AS rheology_as
                    ON rheology_as.sample_id = samples.sample_id
                    AND rheology_as.afterstorage_id = after_storage.afterstorage_id
                LEFT JOIN initial_tack
                    ON initial_tack.sample_id = samples.sample_id
                LEFT JOIN skinformation AS skinformation_normal
                    ON skinformation_normal.sample_id = samples.sample_id
                    AND skinformation_normal.afterstorage_id IS NULL
                LEFT JOIN skinformation AS skinformation_as
                    ON skinformation_as.sample_id = samples.sample_id
                    AND skinformation_as.afterstorage_id = after_storage.afterstorage_id
                LEFT JOIN curability AS curability_normal
                    ON curability_normal.sample_id = samples.sample_id
                    AND curability_normal.afterstorage_id IS NULL
                LEFT JOIN curability AS curability_as
                    ON curability_as.sample_id = samples.sample_id
                    AND curability_as.afterstorage_id = after_storage.afterstorage_id
                LEFT JOIN shore_a
                    ON shore_a.sample_id = samples.sample_id
                LEFT JOIN density
                    ON density.sample_id = samples.sample_id
                LEFT JOIN adhesion
                    ON adhesion.sample_id = samples.sample_id
                LEFT JOIN tensile_specimen
                    ON tensile_specimen.sample_id = samples.sample_id
                LEFT JOIN epdm_adhesion
                    ON epdm_adhesion.sample_id = samples.sample_id
                WHERE samples.product_id = %s
                """
                
            query_args = [product_id]

            if batch_nr:
                query += """
                    AND samples.batch_nr ILIKE %s
                """

                query_args.append(f"%{batch_nr}%")

            if date_from and date_to:
                query += """
                    AND samples.prod_date
                    BETWEEN %s AND %s
                """

                query_args.extend([date_from, date_to])

            elif date_from:
                query += """
                    AND samples.prod_date >= %s
                """

                query_args.append(date_from)

            elif date_to:
                query += """
                    AND samples.prod_date <= %s
                """

                query_args.append(date_to)

            query += """
                GROUP BY
                    samples.sample_id,
                    samples.batch_nr,
                    samples.prod_date,
                    rheology_normal.yield_stress,
                    rheology_normal.vis_at_10,
                    rheology_as.yield_stress,
                    rheology_as.vis_at_10,
                    initial_tack.initial_tack,
                    skinformation_normal.tack_free_time,
                    skinformation_normal.skinformation_time,
                    skinformation_as.tack_free_time,
                    skinformation_as.skinformation_time,
                    curability_normal.day_1,
                    curability_normal.day_7,
                    curability_as.day_1,
                    curability_as.day_7,
                    shore_a.shore_a_avg,
                    density.density_product,
                    adhesion.sample_id,
                    epdm_adhesion.sample_id
                ORDER BY samples.sample_id
                """

            cursor.execute(query, tuple(query_args))

            return cursor.fetchall()

        finally:
            cursor.close()
            connection.close()

    def get_rheology_details(self, sample_id, afterstorage=False):
        connection = get_connection()
        cursor = get_dict_cursor(connection)

        try:
            if afterstorage:
                cursor.execute(
                    """
                    SELECT
                        users.name AS operator,
                        rheology.test_date,
                        rheology.remark,
                        rheology.humidity,
                        rheology.vis_at_1,
                        rheology.vis_at_5,
                        rheology.vis_at_10
                    FROM rheology
                    JOIN users 
                    ON users.user_id = rheology.operator_id
                    WHERE rheology.sample_id = %s
                    AND rheology.afterstorage_id IS NOT NULL
                    """,
                    (sample_id,)
                )

            else:
                cursor.execute(
                    """
                    SELECT
                        users.name AS operator,
                        rheology.test_date,
                        rheology.remark,
                        rheology.humidity,
                        rheology.vis_at_1,
                        rheology.vis_at_5,
                        rheology.vis_at_10
                    FROM rheology
                    JOIN users
                    ON users.user_id = rheology.operator_id
                    WHERE rheology.sample_id = %s
                    AND rheology.afterstorage_id IS NULL
                    """,
                    (sample_id,)
                )

            row = cursor.fetchone()

            if not row: 
                return {}

            return{
                "operator": row["operator"],
                "test_date":( 
                    row["test_date"].strftime("%d-%m-%Y %H:%M") 
                    if row["test_date"]
                    else "" 
                ),
                "remark": row["remark"] or "",
                "environment": {
                    "humidity": row["humidity"]
                },
                "details": [ 
                    {
                        "name": "Vis @ 1",
                        "value": row["vis_at_1"]
                    },
                    {
                        "name": "Vis @ 5",
                        "value": row["vis_at_5"]
                    },
                    {

                    "name": "Vis @ 10",
                    "value": row["vis_at_10"]
                    } 
                ]
            }

        finally:
            cursor.close()
            connection.close()


    def get_shore_a_details(self, sample_id):
        connection = get_connection()
        cursor = get_dict_cursor(connection)

        try:
            cursor.execute(
                """
                SELECT
                    users.name AS operator,
                    shore_a.test_date,
                    shore_a.humidity,
                    shore_a.temperature,
                    shore_a.remark,
                    shore_a.shore_a_1,
                    shore_a.shore_a_2,
                    shore_a.shore_a_3
                FROM shore_a
                JOIN users
                ON users.user_id = shore_a.operator_id
                WHERE shore_a.sample_id = %s
                """,
                (sample_id,)
            )

            row = cursor.fetchone()

            if not row:
                return {}

            return {
                "operator": row["operator"],

                "test_date": (
                    row["test_date"].strftime("%d-%m-%Y %H:%M")
                    if row["test_date"]
                    else ""
                ),

                "remark": row["remark"],

                "environment": {
                    "Temperature": row["temperature"],
                    "Humidity": row["humidity"]
                },

                "details":[
                    {
                        "name": "Shore A 1",
                        "value": row["shore_a_1"]
                    },
                    {
                        "name": "Shore A 2",
                        "value": row["shore_a_2"]
                    },
                    {
                        "name": "Shore A 3",
                        "value": row["shore_a_3"]
                    }
                ]
            }

        finally:
            cursor.close()
            connection.close()

    def get_initial_tack_details(self, sample_id):
        connection = get_connection()
        cursor = get_dict_cursor(connection)

        try:
            cursor.execute(
                """
                SELECT
                    users.name AS operator,
                    initial_tack.test_date,
                    initial_tack.remark,
                    initial_tack.humidity,
                    initial_tack.area,
                    initial_tack.area_weight,
                    initial_tack.added_weight
                FROM initial_tack
                JOIN users
                ON users.user_id = initial_tack.operator_id
                WHERE sample_id = %s
                """,
                (sample_id,)
            )

            row = cursor.fetchone()

            if not row:
                return {}

            return {
                "operator": row["operator"],

                "test_date": (
                    row["test_date"].strftime("%d-%m-%Y %H:%M")
                    if row["test_date"]
                    else ""
                ),

                "remark": row["remark"],

                "environment": {
                    "Humidity": row["humidity"]
                },

                "details":[
                    {
                        "name": "Oppervlak",
                        "value": row["area"]
                    },
                    {
                        "name": "Gewicht opp.",
                        "value": row["area_weight"]
                    },
                    {
                        "name": "Toegevoegd gewicht",
                        "value": row["added_weight"]
                    }
                ]
            }

        finally:
            cursor.close()
            connection.close()

    def get_tack_free_details(self, sample_id, afterstorage=False):
        connection = get_connection()
        cursor = get_dict_cursor(connection)

        try:
            if afterstorage:
                cursor.execute(
                    """
                    SELECT
                        users.name AS operator,
                        skinformation.test_date,
                        skinformation.remark,
                        skinformation.temp_tack_free_time,
                        skinformation.rh_tack_free_time
                    FROM skinformation
                    JOIN users 
                    ON users.user_id = skinformation.operator_id
                    WHERE skinformation.sample_id = %s
                    AND skinformation.afterstorage_id IS NOT NULL
                    """,
                    (sample_id,)
                )

            else:
                cursor.execute(
                    """
                    SELECT
                        users.name AS operator,
                        skinformation.test_date,
                        skinformation.remark,
                        skinformation.temp_tack_free_time,
                        skinformation.rh_tack_free_time
                    FROM skinformation
                    JOIN users 
                    ON users.user_id = skinformation.operator_id
                    WHERE skinformation.sample_id = %s
                    AND skinformation.afterstorage_id IS NULL
                    """,
                    (sample_id,)
                )

            row = cursor.fetchone()

            if not row: 
                return {}

            return{
                "operator": row["operator"],
                "test_date":( 
                    row["test_date"].strftime("%d-%m-%Y %H:%M") 
                    if row["test_date"]
                    else "" 
                ),
                "remark": row["remark"] or "",
                "environment": {
                    "Temperature": row["temp_tack_free_time"],
                    "Humidity": row["rh_tack_free_time"]
                },
                "details": []
            }

        finally:
            cursor.close()
            connection.close()

    def get_skinformation_details(self, sample_id, afterstorage=False):
        connection = get_connection()
        cursor = get_dict_cursor(connection)

        try:
            if afterstorage:
                cursor.execute(
                    """
                    SELECT
                        users.name AS operator,
                        skinformation.test_date,
                        skinformation.remark,
                        skinformation.temp_skinformation_time,
                        skinformation.rh_skinformation_time
                    FROM skinformation
                    JOIN users 
                    ON users.user_id = skinformation.operator_id
                    WHERE skinformation.sample_id = %s
                    AND skinformation.afterstorage_id IS NOT NULL
                    """,
                    (sample_id,)
                )

            else:
                cursor.execute(
                    """
                    SELECT
                        users.name AS operator,
                        skinformation.test_date,
                        skinformation.remark,
                        skinformation.temp_skinformation_time,
                        skinformation.rh_skinformation_time
                    FROM skinformation
                    JOIN users 
                    ON users.user_id = skinformation.operator_id
                    WHERE skinformation.sample_id = %s
                    AND skinformation.afterstorage_id IS NULL
                    """,
                    (sample_id,)
                )

            row = cursor.fetchone()

            if not row: 
                return {}

            return{
                "operator": row["operator"],
                "test_date":( 
                    row["test_date"].strftime("%d-%m-%Y %H:%M") 
                    if row["test_date"]
                    else "" 
                ),
                "remark": row["remark"] or "",
                "environment": {
                    "Temperature": row["temp_skinformation_time"],
                    "Humidity": row["rh_skinformation_time"]
                },
                "details": []
            }

        finally:
            cursor.close()
            connection.close()

    def get_curabilityday1_details(self, sample_id, afterstorage=False):
        connection = get_connection()
        cursor = get_dict_cursor(connection)

        try:
            if afterstorage:
                cursor.execute(
                    """
                    SELECT
                        users.name AS operator,
                        curability.test_date,
                        curability.remark,
                        curability.temp_day1,
                        curability.rh_day1
                    FROM curability
                    JOIN users 
                    ON users.user_id = curability.operator_id
                    WHERE curability.sample_id = %s
                    AND curability.afterstorage_id IS NOT NULL
                    """,
                    (sample_id,)
                )

            else:
                cursor.execute(
                    """
                    SELECT
                        users.name AS operator,
                        curability.test_date,
                        curability.remark,
                        curability.temp_day1,
                        curability.rh_day1
                    FROM curability
                    JOIN users 
                    ON users.user_id = curability.operator_id
                    WHERE curability.sample_id = %s
                    AND curability.afterstorage_id IS NULL
                    """,
                    (sample_id,)
                )

            row = cursor.fetchone()

            if not row: 
                return {}

            return{
                "operator": row["operator"],
                "test_date":( 
                    row["test_date"].strftime("%d-%m-%Y %H:%M") 
                    if row["test_date"]
                    else "" 
                ),
                "remark": row["remark"] or "",
                "environment": {
                    "Temperature": row["temp_day1"],
                    "Humidity": row["rh_day1"]
                },
                "details": []
            }

        finally:
            cursor.close()
            connection.close()

    def get_curabilityday7_details(self, sample_id, afterstorage=False):
        connection = get_connection()
        cursor = get_dict_cursor(connection)

        try:
            if afterstorage:
                cursor.execute(
                    """
                    SELECT
                        users.name AS operator,
                        curability.test_date,
                        curability.remark,
                        curability.temp_day7,
                        curability.rh_day7
                    FROM curability
                    JOIN users 
                    ON users.user_id = curability.operator_id
                    WHERE curability.sample_id = %s
                    AND curability.afterstorage_id IS NOT NULL
                    """,
                    (sample_id,)
                )

            else:
                cursor.execute(
                    """
                    SELECT
                        users.name AS operator,
                        curability.test_date,
                        curability.remark,
                        curability.temp_day7,
                        curability.rh_day7
                    FROM curability
                    JOIN users 
                    ON users.user_id = curability.operator_id
                    WHERE curability.sample_id = %s
                    AND curability.afterstorage_id IS NULL
                    """,
                    (sample_id,)
                )

            row = cursor.fetchone()

            if not row: 
                return {}

            return{
                "operator": row["operator"],
                "test_date":( 
                    row["test_date"].strftime("%d-%m-%Y %H:%M") 
                    if row["test_date"]
                    else "" 
                ),
                "remark": row["remark"] or "",
                "environment": {
                    "Temperature": row["temp_day7"],
                    "Humidity": row["rh_day7"]
                },
                "details": []
            }

        finally:
            cursor.close()
            connection.close()

    def get_density_details(self, sample_id):
        connection = get_connection()
        cursor = get_dict_cursor(connection)

        try:
            cursor.execute(
                """
                SELECT
                    users.name AS operator,
                    density.test_date,
                    density.remark,
                    density.vessel_empty,
                    density.vessel_full
                FROM density
                JOIN users
                ON users.user_id = density.operator_id
                WHERE sample_id = %s
                """,
                (sample_id,)
            )

            row = cursor.fetchone()

            if not row:
                return {}

            return {
                "operator": row["operator"],

                "test_date": (
                    row["test_date"].strftime("%d-%m-%Y %H:%M")
                    if row["test_date"]
                    else ""
                ),

                "remark": row["remark"],

                "environment": {},

                "details":[
                    {
                        "name": "Gewicht leeg",
                        "value": row["vessel_empty"]
                    },
                    {
                        "name": "Gewicht vol",
                        "value": row["vessel_full"]
                    },
                ]
            }

        finally:
            cursor.close()
            connection.close()

    def get_adhesion_details(self, sample_id):
        connection = get_connection()
        cursor = get_dict_cursor(connection)

        try:
            cursor.execute(
                """
                SELECT
                    users.name AS operator,
                    adhesion.test_date,
                    adhesion.remark,
                    adhesion.rubber,
                    adhesion.copper,
                    adhesion.wood,
                    adhesion.aluminium,
                    adhesion.aluminium_anod,
                    adhesion.rvs,
                    adhesion.lead,
                    adhesion.concrete,
                    adhesion.glass,
                    adhesion.pvc,
                    adhesion.pmma,
                    adhesion.pc
                FROM adhesion
                JOIN users
                ON users.user_id = adhesion.operator_id
                WHERE sample_id = %s
                """,
                (sample_id,)
            )

            row = cursor.fetchone()

            if not row:
                return {}

            return {
                "operator": row["operator"],

                "test_date": (
                    row["test_date"].strftime("%d-%m-%Y %H:%M")
                    if row["test_date"]
                    else ""
                ),

                "remark": row["remark"],

                "environment": {},

                "details":[
                    {
                        "name": "Rubber",
                        "value": row["rubber"]
                    },
                    {
                        "name": "Koper",
                        "value": row["copper"]
                    },
                    {
                        "name": "Hout",
                        "value": row["wood"]
                    },
                    {
                        "name": "Aluminium",
                        "value": row["aluminium"]
                    },
                    {
                        "name": "Aluminium Anod",
                        "value": row["aluminium_anod"]
                    },
                    {
                        "name": "Lood",
                        "value": row["lead"]
                    },
                    {
                        "name": "RVS",
                        "value": row["rvs"]
                    },
                    {
                        "name": "Beton",
                        "value": row["concrete"]
                    },
                    {
                        "name": "Glas",
                        "value": row["glass"]
                    },
                    {
                        "name": "PVC",
                        "value": row["pvc"]
                    },
                    {
                        "name": "PMMA",
                        "value": row["pmma"]
                    },
                    {
                        "name": "PC",
                        "value": row["pc"]
                    },
                ]
            }

        finally:
            cursor.close()
            connection.close()

    def get_epdm_adhesion_details(self, sample_id):
        connection = get_connection()
        cursor = get_dict_cursor(connection)

        try:
            cursor.execute(
                """
                SELECT
                    users.name AS operator,
                    epdm_adhesion.test_date,
                    epdm_adhesion.remark,
                    epdm_adhesion.europees,
                    epdm_adhesion.trc,
                    epdm_adhesion.carlisle,
                    epdm_adhesion.rubber,
                    epdm_adhesion.copper,
                    epdm_adhesion.wood,
                    epdm_adhesion.aluminium,
                    epdm_adhesion.aluminium_anod,
                    epdm_adhesion.rvs,
                    epdm_adhesion.lead,
                    epdm_adhesion.concrete,
                    epdm_adhesion.glass,
                    epdm_adhesion.pvc,
                    epdm_adhesion.pmma,
                    epdm_adhesion.pc
                FROM epdm_adhesion
                JOIN users
                ON users.user_id = epdm_adhesion.operator_id
                WHERE sample_id = %s
                """,
                (sample_id,)
            )

            row = cursor.fetchone()

            if not row:
                return {}

            return {
                "operator": row["operator"],

                "test_date": (
                    row["test_date"].strftime("%d-%m-%Y %H:%M")
                    if row["test_date"]
                    else ""
                ),

                "remark": row["remark"],

                "environment": {},

                "details":[
                    {
                        "name": "EPDM-Europees",
                        "value": row["europees"]
                    },
                    {
                        "name": "EPDM-TRC",
                        "value": row["trc"]
                    },
                    {
                        "name": "EPDM-Carlisle",
                        "value": row["carlisle"]
                    },
                    {
                        "name": "Rubber",
                        "value": row["rubber"]
                    },
                    {
                        "name": "Koper",
                        "value": row["copper"]
                    },
                    {
                        "name": "Hout",
                        "value": row["wood"]
                    },
                    {
                        "name": "Aluminium",
                        "value": row["aluminium"]
                    },
                    {
                        "name": "Aluminium Anod",
                        "value": row["aluminium_anod"]
                    },
                    {
                        "name": "Lood",
                        "value": row["lead"]
                    },
                    {
                        "name": "RVS",
                        "value": row["rvs"]
                    },
                    {
                        "name": "Beton",
                        "value": row["concrete"]
                    },
                    {
                        "name": "Glas",
                        "value": row["glass"]
                    },
                    {
                        "name": "PVC",
                        "value": row["pvc"]
                    },
                    {
                        "name": "PMMA",
                        "value": row["pmma"]
                    },
                    {
                        "name": "PC",
                        "value": row["pc"]
                    },
                ]
            }

        finally:
            cursor.close()
            connection.close()

    def get_batch_details(self, sample_id):
        connection = get_connection()
        cursor = get_dict_cursor(connection)

        try:
            cursor.execute(
                """
                SELECT
                    remark
                FROM samples
                WHERE sample_id = %s
                """,
                (sample_id,)
            )

            row = cursor.fetchone()

            if not row:
                return {}

            return {
                "remark": row["remark"],
            }

        finally:
            cursor.close()
            connection.close()

    def get_tensile_details(self, sample_id):
        connection = get_connection()
        cursor = get_dict_cursor(connection)

        try:
            cursor.execute(
                """
                SELECT 
                    users.name AS operator,
                    tensile_strength.test_date,
                    tensile.strength.remark
                FROM tensile_strenght
                JOIN users
                ON users.user_id = tensile_strength.operator_id
                WHERE tensile_strength.sample_id = %s
                """,
                (sample_id,)
            )

            test = cursor.fetchone()

            if not test:
                return {}

            cursor.execute(
                """
                SELECT
                    t_50,
                    t_100,
                    t_max,
                    e_max,
                    remark
                FROM tensile_specimen
                WHERE tensile_specimen.sample_id = %s
                """,
                (sample_id,)
            )

            specimens = cursor.fetchone()

            details = []

            for index, specimen in enumerate(specimens, start=1):
                details.append({
                    "name": f"Dumbel {index} - T_50",
                    "value": specimen["t_50"]
                })

                details.append({
                    "name": f"Dumbel {index} - T_100",
                    "value": specimen["t_100"]
                })

                details.append({
                    "name": f"Dumbel {index} - T_max",
                    "value": specimen["t_max"]
                })

                details.append({
                    "name": f"Dumbel {index} - E_max",
                    "value": specimen["e_max"]
                })

                details.append({
                    "name": f"Dumbel {index} - Opmerking",
                    "value": specimen["remark"]
                })

            return {
                "operator": test["operator"],

                "test_date": (
                    test["test_date"].strftime("%d-%m-%Y %H:%M")
                ),

                "details": details
            }

        finally:
            cursor.close()
            connection.close()

               