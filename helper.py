from functools import wraps
import json
import string
import secrets
from flask import session, redirect, url_for
from decimal import Decimal

def convert_decimal(obj):
    if isinstance(obj, Decimal):
        return float(obj)
    raise TypeError

def login_required(function):

    @wraps(function)
    def wrapper(*args, **kwargs):

        if "user_id" not in session:
            return redirect(
                url_for("login")
            )

        return function(*args, **kwargs)

    return wrapper

def admin_required(function):

    @wraps(function)
    def wrapper(*args, **kwargs):

        if session.get("role") != "admin":
            return redirect(url_for("dashboard"))

        return function(*args, **kwargs)

    return wrapper

def generate_temp_password(length=10):

    characters = (
        string.ascii_letters +
        string.digits +
        "!@#$%"
    )

    password = "".join(
        secrets.choice(characters)
        for _ in range(length)
    )

    return password

def format_datetime(value):
    if value:
        return value.strftime("%d-%m-%Y %H:%M")
    return ""

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