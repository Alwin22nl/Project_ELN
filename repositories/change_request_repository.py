from database import get_connection, get_dict_cursor

from psycopg2 import sql
from psycopg2.extras import Json


class ChangeRequestRepository:
    def create_request(self, change_request):
        connection = get_connection()
        cursor = connection.cursor()

        try:
            cursor.execute(
                """
                INSERT INTO change_requests
                (
                    requested_by,
                    sample_id,
                    table_name,
                    record_id,
                    field_name,
                    old_value,
                    new_value,
                    reason
                )
                VALUES
                (%s,%s,%s,%s,%s,%s,%s)
                RETURNING change_request_id
                """,
                (
                    change_request.requested_by,
                    change_request.sample_id,
                    change_request.table_name,
                    change_request.record_id,
                    change_request.field_name,
                    change_request.old_value,
                    change_request.new_value,
                    change_request.reason
                )
            )

            change_request_id = cursor.fetchone()[0]

            connection.commit()

            return change_request_id

        except Exception:
            connection.rollback()
            raise

        finally:
            cursor.close()
            connection.close()

    def get_batch_nr(self, sample_id):
        connection = get_connection()
        cursor = connection.cursor()

        try:
            cursor.execute(
                """
                SELECT batch_nr
                FROM samples
                WHERE sample_id = %s
                """,
                (sample_id,)
            )

            result = cursor.fetchone()

            if result is None:
                return None

            return result[0]

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
                    product_name
                FROM products
                ORDER BY product_name
                """
            )

            return cursor.fetchall()

        finally:
            cursor.close()
            connection.close()


    def get_batches(self, product_id):
        connection = get_connection()
        cursor = get_dict_cursor(connection)

        try:
            cursor.execute(
                """
                SELECT
                    sample_id,
                    batch_nr
                FROM samples
                WHERE product_id = %s
                ORDER BY sample_id DESC
                """,
                (product_id,)
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
                    specimen_no
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

    def get_test_records(
        self,
        table_name,
        id_column,
        sample_id,
        has_afterstorage
    ):
        connection = get_connection()
        cursor = get_dict_cursor(connection)

        try:
            if has_afterstorage:
                query = sql.SQL(
                    """
                    SELECT
                        {id_column} AS record_id,
                        afterstorage_id
                    FROM {table_name}
                    WHERE sample_id = %s
                    ORDER BY {id_column}
                    """
                ).format(
                    id_column=sql.Identifier(id_column),
                    table_name=sql.Identifier(table_name)
                )

            else:

                query = sql.SQL(
                    """
                    SELECT
                        {id_column} AS record_id,
                        NULL::INTEGER AS afterstorage_id
                    FROM {table_name}
                    WHERE sample_id = %s
                    ORDER BY {id_column}
                    """
                ).format(
                    id_column=sql.Identifier(id_column),
                    table_name=sql.Identifier(table_name)
                )

            cursor.execute(
                query,
                (sample_id,)
            )

            return cursor.fetchall()

        finally:
            cursor.close()
            connection.close()

    def get_test_fields(
        self,
        table_name,
        id_column,
        record_id,
        field_names
    ):
        connection = get_connection()
        cursor = get_dict_cursor(connection)

        try:
            columns = sql.SQL(", ").join(
                sql.Identifier(field)
                for field in field_names
            )

            query = sql.SQL(
                """
                SELECT {columns}
                FROM {table_name}
                WHERE {id_column} = %s
                """
            ).format(
                columns=columns,
                table_name=sql.Identifier(table_name),
                id_column=sql.Identifier(id_column)
            )

            cursor.execute(
                query,
                (record_id,)
            )

            return cursor.fetchone()

        finally:
            cursor.close()
            connection.close()


    def get_current_value(
        self,
        table_name,
        id_column,
        record_id,
        sample_id,
        field_name
    ):
        connection = get_connection()
        cursor = get_dict_cursor(connection)

        try:
            query = sql.SQL(
                """
                SELECT {field_name} AS current_value
                FROM {table_name}
                WHERE {id_column} = %s
                  AND sample_id = %s
                """
            ).format(
                field_name=sql.Identifier(field_name),
                table_name=sql.Identifier(table_name),
                id_column=sql.Identifier(id_column)
            )

            cursor.execute(
                query,
                (
                    record_id,
                    sample_id
                )
            )

            result = cursor.fetchone()

            if result is None:
                return None

            return result["current_value"]

        finally:
            cursor.close()
            connection.close()

    def get_requests_by_user(self, user_id):
        connection = get_connection()
        cursor = get_dict_cursor(connection)

        try:
            cursor.execute(
                """
                SELECT
                    cr.change_request_id,
                    cr.table_name,
                    cr.sample_id,
                    s.batch_nr,
                    cr.record_id,
                    cr.field_name,
                    cr.old_value,
                    cr.new_value,
                    cr.reason,
                    cr.status,
                    cr.requested_at,
                    cr.reviewed_at,
                    cr.review_comment
                FROM change_requests AS cr
                LEFT JOIN samples AS s
                ON s.sample_id = cr.sample_id
                WHERE cr.requested_by = %s
                ORDER BY cr.requested_at DESC, cr.change_request_id DESC
                """,
                (user_id,)
            )

            return cursor.fetchall()

        finally:
            cursor.close()
            connection.close()

    def get_pending_requests(self, reviewer_id):
        connection = get_connection()
        cursor = get_dict_cursor(connection)

        try:
            cursor.execute(
                """
                SELECT
                    cr.change_request_id,
                    cr.sample_id,
                    s.batch_nr,
                    cr.requested_by,
                    u.name AS requested_by_name,
                    cr.table_name,
                    cr.record_id,
                    cr.field_name,
                    cr.old_value,
                    cr.new_value,
                    cr.reason,
                    cr.status,
                    cr.requested_at
                FROM change_requests AS cr
                JOIN users AS u
                ON u.user_id = cr.requested_by
                LEFT JOIN samples AS s
                ON s.sample_id = cr.sample_id
                WHERE cr.status = 'pending'
                  AND cr.requested_by <> %s
                ORDER BY cr.requested_at ASC
                """,
                (reviewer_id,)
            )

            return cursor.fetchall()

        finally:
            cursor.close()
            connection.close()

    def review_request(
        self,
        change_request_id,
        status,
        reviewed_by,
        review_comment
    ):
        connection = get_connection()
        cursor = connection.cursor()

        try:
            cursor.execute(
                """
                UPDATE change_requests
                SET
                    status = %s,
                    reviewed_by = %s,
                    reviewed_at = CURRENT_TIMESTAMP,
                    review_comment = %s
                WHERE change_request_id = %s
                  AND status = 'pending'
                  AND requested_by <> %s
                RETURNING change_request_id
                """,
                (
                    status,
                    reviewed_by,
                    review_comment,
                    change_request_id,
                    reviewed_by
                )
            )

            updated = cursor.fetchone()

            if updated is None:
                connection.rollback()
                return False

            connection.commit()

            return True

        except Exception:
            connection.rollback()
            raise

        finally:
            cursor.close()
            connection.close()

    def get_request(self, change_request_id):
        connection = get_connection()
        cursor = get_dict_cursor(connection)

        try:
            cursor.execute(
                """
                SELECT
                    change_request_id,
                    requested_by,
                    table_name,
                    record_id,
                    field_name,
                    old_value,
                    new_value,
                    reason,
                    status
                FROM change_requests
                WHERE change_request_id = %s
                """,
                (change_request_id,)
            )

            return cursor.fetchone()

        finally:
            cursor.close()
            connection.close()

    def approve_and_apply_change(
        self,
        change_request_id,
        reviewer_id,
        table_name,
        id_column,
        field_name,
        review_comment,
        recalculate=None
    ):
        connection = get_connection()
        cursor = get_dict_cursor(connection)

        try:
            cursor.execute(
                """
                SELECT
                    change_request_id,
                    requested_by,
                    table_name,
                    record_id,
                    field_name,
                    old_value,
                    new_value,
                    reason,
                    status
                FROM change_requests
                WHERE change_request_id = %s
                FOR UPDATE
                """,
                (change_request_id,)
            )

            change = cursor.fetchone()

            if change is None:
                raise ValueError(
                    "Wijzigingsaanvraag bestaat niet."
                )

            if change["status"] != "pending":
                raise ValueError(
                    "Deze wijzigingsaanvraag is al behandeld."
                )

            if change["requested_by"] == reviewer_id:
                raise ValueError(
                    "Je kunt je eigen wijzigingsaanvraag niet goedkeuren."
                )

            if change["table_name"] != table_name:
                raise ValueError(
                    "Ongeldige tabel voor deze wijziging."
                )

            if change["field_name"] != field_name:
                raise ValueError(
                    "Ongeldig veld voor deze wijziging."
                )

            query = sql.SQL(
                """
                SELECT {field}
                FROM {table}
                WHERE {id_column} = %s
                FOR UPDATE
                """
            ).format(
                field=sql.Identifier(field_name),
                table=sql.Identifier(table_name),
                id_column=sql.Identifier(id_column)
            )

            cursor.execute(
                query,
                (change["record_id"],)
            )

            current_record = cursor.fetchone()

            if current_record is None:
                raise ValueError(
                    "Het oorspronkelijke testresultaat bestaat niet meer."
                )

            current_value = current_record[field_name]

            current_text = (
                None
                if current_value is None
                else str(current_value)
            )

            stored_old_text = (
                None
                if change["old_value"] is None
                else str(change["old_value"])
            )

            if current_text != stored_old_text:
                raise ValueError(
                    "De oorspronkelijke waarde is inmiddels gewijzigd. "
                    "De aanvraag kan daarom niet automatisch worden uitgevoerd."
                )

            old_values = {
                field_name: current_text
            }

            new_values = {
                field_name: change["new_value"]
            }

            calculated_field = None
            source_fields = None
            calculation_group = None

            if recalculate:
                if (
                    "field" in recalculate
                    and "source_fields" in recalculate
                ):

                    if field_name in recalculate["source_fields"]:

                        calculated_field = recalculate["field"]
                        source_fields = recalculate["source_fields"]

                else:

                    for group_name, rule in recalculate.items():

                        trigger_fields = rule.get(
                            "trigger_fields",
                            []
                        )

                        if field_name in trigger_fields:

                            calculated_field = rule["result_field"]
                            source_fields = trigger_fields
                            calculation_group = group_name

                            break

            if calculated_field is not None:

                calculated_query = sql.SQL(
                    """
                    SELECT {calculated_field}
                    FROM {table}
                    WHERE {id_column} = %s
                    """
                ).format(
                    calculated_field=sql.Identifier(
                        calculated_field
                    ),
                    table=sql.Identifier(table_name),
                    id_column=sql.Identifier(id_column)
                )

                cursor.execute(
                    calculated_query,
                    (change["record_id"],)
                )

                calculated_record = cursor.fetchone()

                if calculated_record is None:
                    raise ValueError(
                        "De berekende waarde kon niet worden gevonden."
                    )

                old_calculated_value = calculated_record[
                    calculated_field
                ]

                old_values[calculated_field] = (
                    None
                    if old_calculated_value is None
                    else str(old_calculated_value)
                )

            update_query = sql.SQL(
                """
                UPDATE {table}
                SET {field} = %s
                WHERE {id_column} = %s
                """
            ).format(
                table=sql.Identifier(table_name),
                field=sql.Identifier(field_name),
                id_column=sql.Identifier(id_column)
            )

            cursor.execute(
                update_query,
                (
                    change["new_value"],
                    change["record_id"]
                )
            )

            if calculated_field is not None:

                columns = sql.SQL(", ").join(
                    sql.Identifier(field)
                    for field in source_fields
                )

                source_query = sql.SQL(
                    """
                    SELECT {columns}
                    FROM {table}
                    WHERE {id_column} = %s
                    """
                ).format(
                    columns=columns,
                    table=sql.Identifier(table_name),
                    id_column=sql.Identifier(id_column)
                )

                cursor.execute(
                    source_query,
                    (change["record_id"],)
                )

                result = cursor.fetchone()

                if result is None:
                    raise ValueError(
                        "De waarden voor herberekening "
                        "konden niet worden gevonden."
                    )

                if table_name == "shore_a":

                    values = [
                        float(result[field])
                        for field in source_fields
                    ]

                    new_calculated_value = round(
                        sum(values) / len(values),
                        0
                    )

                elif table_name == "density":

                    vessel_full = float(
                        result["vessel_full"]
                    )

                    vessel_empty = float(
                        result["vessel_empty"]
                    )

                    vessel_volume = float(
                        result["vessel_volume"]
                    )

                    if vessel_volume == 0:
                        raise ValueError(
                            "Vessel volume kan niet 0 zijn."
                        )

                    new_calculated_value = round(
                        (
                            vessel_full
                            - vessel_empty
                        )
                        / vessel_volume,
                        2
                    )

                elif table_name == "initial_tack":

                    area = float(
                        result["area"]
                    )

                    area_weight = float(
                        result["area_weight"]
                    )

                    added_weight = float(
                        result["added_weight"]
                    )

                    if area == 0:
                        raise ValueError(
                            "Oppervlakte kan niet 0 zijn."
                        )

                    new_calculated_value = round(
                        (
                            area_weight
                            + added_weight
                        )
                        / area,
                        2
                    )

                elif table_name == "tensile_specimen":

                    values = [
                        float(result[field])
                        for field in source_fields
                    ]

                    tensile_rule = recalculate[
                        calculation_group
                    ]

                    decimal_places = tensile_rule.get(
                        "round",
                        2
                    )

                    new_calculated_value = round(
                        sum(values) / len(values),
                        decimal_places
                    )

                else:
                    raise ValueError(
                        f"Geen herberekening ingesteld voor "
                        f"tabel '{table_name}'."
                    )

                calculated_update = sql.SQL(
                    """
                    UPDATE {table}
                    SET {calculated_field} = %s
                    WHERE {id_column} = %s
                    """
                ).format(
                    table=sql.Identifier(table_name),
                    calculated_field=sql.Identifier(
                        calculated_field
                    ),
                    id_column=sql.Identifier(id_column)
                )

                cursor.execute(
                    calculated_update,
                    (
                        new_calculated_value,
                        change["record_id"]
                    )
                )

                new_values[calculated_field] = str(
                    new_calculated_value
                )

            cursor.execute(
                """
                INSERT INTO audit_log
                (
                    table_name,
                    record_id,
                    changed_by,
                    changed_at,
                    old_values,
                    new_values,
                    reason
                )
                VALUES
                (
                    %s,
                    %s,
                    %s,
                    CURRENT_TIMESTAMP,
                    %s,
                    %s,
                    %s
                )
                """,
                (
                    table_name,
                    change["record_id"],
                    reviewer_id,
                    Json(old_values),
                    Json(new_values),
                    change["reason"]
                )
            )

            cursor.execute(
                """
                UPDATE change_requests
                SET
                    status = 'approved',
                    reviewed_by = %s,
                    reviewed_at = CURRENT_TIMESTAMP,
                    review_comment = %s
                WHERE change_request_id = %s
                """,
                (
                    reviewer_id,
                    review_comment,
                    change_request_id
                )
            )

            connection.commit()


        except Exception:
            connection.rollback()
            raise

        finally:
            cursor.close()
            connection.close()

    def has_open_requests_for_user(self, user_id):
        connection = get_connection()
        cursor = connection.cursor()

        try:
            cursor.execute(
                """
                SELECT EXISTS (
                    SELECT 1
                    FROM change_requests
                    WHERE status = 'pending'
                    AND requested_by <> %s
                )
                """,
                (user_id,)
            )

            return cursor.fetchone()[0]

        finally:
            cursor.close()
            connection.close()