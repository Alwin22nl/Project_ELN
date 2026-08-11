import json
from flask import session
from decimal import Decimal

def convert_decimal(obj):
    if isinstance(obj, Decimal):
        return float(obj)
    raise TypeError

def log_change(
        cursor,
        table_name,
        record_id,
        old_values,
        new_values,
        reason
    ):

    cursor.execute("""
        INSERT INTO audit_log (
            table_name,
            record_id,
            changed_by,
            old_values,
            new_values,
            reason
        )
        VALUES (%s,%s,%s,%s,%s,%s)
    """,
    (
        table_name,
        record_id,
        session["user_id"],
        json.dumps(old_values, default=convert_decimal),
        json.dumps(new_values, default=convert_decimal),
        reason
    ))