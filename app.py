# import full library's
import os
import secrets
import string
import calendar
import re

# import partial library's
from dotenv import load_dotenv
from flask import session, Flask, render_template, request, redirect, url_for, jsonify
from database import get_connection, get_dict_cursor
from datetime import date, timedelta, datetime
from numbers import Real
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps

# importing other Py files
from config.test import TEST_PAGES, OVERVIEW_TESTS
from helper import log_change, login_required, admin_required, generate_temp_password, format_datetime

#importing routes
from routes.authentication import authentication_bp
from routes.admin import admin_bp
from routes.samples import sample_bp
from routes.dashboard import dashboard_bp
from routes.products import product_bp

# importing Test Routes
from routes.tests import test_bp
from routes.rheology import rheology_bp
from routes.skinformation import skinformation_bp
from routes.initial_tack import initial_tack_bp
from routes.density import density_bp
from routes.shore_a import shore_a_bp
from routes.adhesion import adhesion_bp
from routes.epdm_adhesion import epdm_adhesion_bp
from routes.curability import curability_bp
from routes.tensile import tensile_bp

load_dotenv()
today = date.today()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")
app.permanent_session_lifetime = timedelta(hours=1)
app.config["SESSION_REFRESH_EACH_REQUEST"] = True

# routes
app.register_blueprint(authentication_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(sample_bp)
app.register_blueprint(dashboard_bp)
app.register_blueprint(product_bp)

# test routes
app.register_blueprint(test_bp)
app.register_blueprint(rheology_bp)
app.register_blueprint(skinformation_bp)
app.register_blueprint(initial_tack_bp)
app.register_blueprint(density_bp)
app.register_blueprint(shore_a_bp)
app.register_blueprint(adhesion_bp)
app.register_blueprint(epdm_adhesion_bp)
app.register_blueprint(curability_bp)
app.register_blueprint(tensile_bp)

@app.route("/overview", methods=["GET", "POST"])
@login_required
def overview_page():

    connection = get_connection()
    cursor = get_dict_cursor(connection)

    # Product dropdown
    cursor.execute("""
        SELECT
            product_id,
            product_name
        FROM products
        ORDER BY product_name
    """)

    products = cursor.fetchall()
    product_id = request.args.get("product_id", type=int)
    batch_nr = request.args.get("batch_nr", "").strip()
    prod_date_from = request.args.get("prod_date_from", "").strip()
    prod_date_to = request.args.get("prod_date_to", "").strip()

    if not product_id:

        cursor.close()
        connection.close()

        return render_template(
            "overview.html",
            products=products,
            selected_product=None,
            columns=[],
            as_columns=[],
            results=[],
            batch_nr="",
            prod_date_from="",
            prod_date_to=""
        )

    # Required tests for this product
    cursor.execute("""
        SELECT test_type_id
        FROM product_test_requirements
        WHERE product_id = %s
        ORDER BY test_type_id
    """, (product_id,))

    required_tests = [row["test_type_id"] for row in cursor.fetchall()]
    columns = [
        ("Batch", "batch_nr"),
        ("Production", "prod_date")
    ]
    as_columns = []
    if 1 in required_tests:
        columns.extend([
            ("Yield Stress", "yield_stress"),
            ("Vis @10", "vis_at_10")
        ])
        # after-storage columns for rheology
        as_columns.extend([
            ("Yield Stress (AS)", "yield_stress_as"),
            ("Vis @10 (AS)", "vis_at_10_as")
        ])

    if 8 in required_tests:
        columns.append(
            ("Initial Tack", "initial_tack")
        )

    if 9 in required_tests:
        columns.extend([
            ("Tack Free", "tack_free_time"),
            ("Skin Formation", "skinformation_time")
        ])
        # after-storage columns for skinformation
        as_columns.extend([
            ("Tack Free (AS)", "tack_free_time_as"),
            ("Skin Formation (AS)", "skinformation_time_as")
        ])

    if 2 in required_tests:
        columns.extend([
            ("Day 1", "day_1"),
            ("Day 7", "day_7")
        ])
        # after-storage columns for curability
        as_columns.extend([
            ("Day 1 (AS)", "day_1_as"),
            ("Day 7 (AS)", "day_7_as")
        ])

    if 3 in required_tests:
        columns.append(
            ("Shore A", "shore_a_avg")
        )

    if 5 in required_tests:
        columns.extend([
            ("Tmax", "t_max"),
            ("Emax", "e_max")
        ])

    if 4 in required_tests:
        columns.append(
            ("Density", "density_product")
        )

    if 6 in required_tests:
        columns.append(
            ("Adhesion", "adhesion")
        )
    
    if 7 in required_tests:
        columns.append(
            ("EPDM Adhesion", "epdm_adhesion")
        )

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
        query += "\n            AND samples.batch_nr ILIKE %s"
        query_args.append(f"%{batch_nr}%")

    # Parse partial date inputs in order: DD-MM-YYYY, MM-YYYY, or YYYY
    def parse_partial(s):
        if not s:
            return None, None
        s = s.strip()
        # DD-MM-YYYY or D-M-YYYY
        m = re.match(r"^(\d{1,2})-(\d{1,2})-(\d{4})$", s)
        if m:
            d = int(m.group(1)); mon = int(m.group(2)); y = int(m.group(3))
            try:
                return date(y, mon, d), date(y, mon, d)
            except Exception:
                return None, None
        # MM-YYYY or M-YYYY
        m = re.match(r"^(\d{1,2})-(\d{4})$", s)
        if m:
            mon = int(m.group(1)); y = int(m.group(2))
            try:
                last = calendar.monthrange(y, mon)[1]
                return date(y, mon, 1), date(y, mon, last)
            except Exception:
                return None, None
        # YYYY
        if re.match(r"^\d{4}$", s):
            y = int(s)
            return date(y, 1, 1), date(y, 12, 31)
        return None, None

    df1, dt1 = parse_partial(prod_date_from)
    df2, dt2 = parse_partial(prod_date_to)
    date_from = df1 or df2
    date_to = dt2 or dt1

    if date_from and date_to:
        query += "\n            AND samples.prod_date BETWEEN %s AND %s"
        query_args.extend([date_from, date_to])
    elif date_from:
        query += "\n            AND samples.prod_date >= %s"
        query_args.append(date_from)
    elif date_to:
        query += "\n            AND samples.prod_date <= %s"
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

    results = cursor.fetchall()

    averages = {}
    for title, field in columns + as_columns:
        values = []
        for row in results:
            try:
                val = row[field]
            except Exception:
                # row may be a tuple-like; skip if we can't access by key
                continue
            if val is None:
                continue
            try:
                f = float(val)
            except Exception:
                # not a numeric value (e.g. strings like '✓'), skip
                continue
            values.append(f)

        averages[field] = round(sum(values) / len(values), 3) if values else None

    cursor.close()
    connection.close()

    return render_template(
        "overview.html",
        products=products,
        selected_product=product_id,
        columns=columns,
        as_columns=as_columns,
        results=results,
        batch_nr=batch_nr,
        prod_date_from=prod_date_from,
        prod_date_to=prod_date_to,
        averages=averages
    )

@app.route("/batch_search", methods=["GET", "POST"])
@login_required
def batch_search():

    connection = get_connection()
    cursor = get_dict_cursor(connection)

    batch = None
    results = []

    if request.method == "POST":
        batch_nr = request.form["batch_nr"]
        cursor.execute("""
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
            WHERE samples.batch_nr = %s

        """,
        (batch_nr,)
        )
        batch = cursor.fetchone()
        if batch:
            sample_id = batch["sample_id"]

            cursor.execute("""
                SELECT test_type_id
                FROM product_test_requirements
                WHERE product_id = %s
            """, (batch["product_id"],))

            required_tests = [
                row["test_type_id"]
                for row in cursor.fetchall()
            ]

            # Rheology
            if 1 in required_tests:
                cursor.execute("""
                    SELECT
                        rheology.yield_stress,
                        rheology.vis_at_1,
                        rheology.vis_at_5,
                        rheology.vis_at_10,
                        rheology.humidity,
                        rheology.test_date, 
                        users.name AS operator
                    FROM rheology
                    JOIN users
                    ON users.user_id = rheology.operator_id
                    WHERE rheology.sample_id = %s

                """,
                (sample_id,)
                )
                rheology = cursor.fetchone()
                if rheology:

                    results.append({
                        "test_name": "Rheology",
                        "operator": rheology["operator"],
                        "test_date": format_datetime(rheology["test_date"]),

                        "values": {
                            "Yield stress": rheology["yield_stress"],
                            "Viscosity @1": rheology["vis_at_1"],
                            "Viscosity @5": rheology["vis_at_5"],
                            "Viscosity @10": rheology["vis_at_10"],
                            "Humidity": rheology["humidity"]
                        }
                    })
                    # also include any after-storage rheology results for this sample
                    cursor.execute("""
                        SELECT
                            rheology.yield_stress,
                            rheology.vis_at_1,
                            rheology.vis_at_5,
                            rheology.vis_at_10,
                            rheology.humidity,
                            rheology.test_date,
                            users.name AS operator
                        FROM rheology
                        JOIN after_storage
                            ON rheology.afterstorage_id = after_storage.afterstorage_id
                        JOIN users
                            ON users.user_id = rheology.operator_id
                        WHERE after_storage.sample_id = %s
                    """,
                    (sample_id,)
                    )
                    for r_as in cursor.fetchall():
                        results.append({
                            "test_name": "Rheology (after storage)",
                            "operator": r_as["operator"],
                            "test_date": format_datetime(r_as["test_date"]),
                            "values": {
                                "Yield stress": r_as["yield_stress"],
                                "Viscosity @1": r_as["vis_at_1"],
                                "Viscosity @5": r_as["vis_at_5"],
                                "Viscosity @10": r_as["vis_at_10"],
                                "Humidity": r_as["humidity"]
                            }
                        })
                else:
                    cursor.execute("""
                        SELECT
                            rheology.yield_stress,
                            rheology.vis_at_1,
                            rheology.vis_at_5,
                            rheology.vis_at_10,
                            rheology.humidity,
                            rheology.test_date,
                            users.name AS operator
                        FROM rheology
                        JOIN after_storage
                            ON rheology.afterstorage_id = after_storage.afterstorage_id
                        JOIN users
                            ON users.user_id = rheology.operator_id
                        WHERE after_storage.sample_id = %s
                    """,
                    (sample_id,)
                    )
                    rheology_as = cursor.fetchone()
                    if rheology_as:
                        results.append({
                            "test_name": "Rheology (after storage)",
                            "operator": rheology_as["operator"],
                            "test_date": format_datetime(rheology_as["test_date"]),
                            "values": {
                                "Yield stress": rheology_as["yield_stress"],
                                "Viscosity @1": rheology_as["vis_at_1"],
                                "Viscosity @5": rheology_as["vis_at_5"],
                                "Viscosity @10": rheology_as["vis_at_10"],
                                "Humidity": rheology_as["humidity"]
                            }
                        })
                    else:
                        results.append({
                            "test_name": "Rheology",
                            "operator": "",
                            "test_date": "",
                            "values": {
                                "Status": "No result recorded"
                            }
                        })

            # Initial Tack
            if 8 in required_tests:
                cursor.execute("""
                    SELECT
                        initial_tack.initial_tack,
                        initial_tack.humidity,
                        initial_tack.test_date, 
                        users.name AS operator
                    FROM initial_tack
                    JOIN users
                    ON users.user_id = initial_tack.operator_id
                    WHERE initial_tack.sample_id = %s
                """,
                (sample_id,)
                )
                initial_tack = cursor.fetchone()
                if initial_tack:

                    results.append({
                        "test_name": "Initial Tack",
                        "operator": initial_tack["operator"],
                        "test_date": format_datetime(initial_tack["test_date"]),

                        "values": {
                            "Initial tack": initial_tack["initial_tack"],
                            "Humidity": initial_tack["humidity"]
                        }
                    })
                else:
                        results.append({
                            "test_name": "Initial Tack",
                            "operator": "",
                            "test_date": "",
                            "values": {
                                "Status": "No result recorded"
                            }
                        })

            # Skinformation
            if 9 in required_tests:
                cursor.execute("""
                    SELECT
                        skinformation.tack_free_time,
                        skinformation.skinformation_time,
                        skinformation.test_date,
                        users.name AS operator
                    FROM skinformation
                    JOIN users
                    ON users.user_id = skinformation.operator_id
                    WHERE skinformation.sample_id = %s
                """,
                (sample_id,)
                )
                skinformation = cursor.fetchone()
                if skinformation:

                    results.append({
                        "test_name": "Skinformation",
                        "operator": skinformation["operator"],
                        "test_date": format_datetime(skinformation["test_date"]),

                        "values": {
                            "Tack free": skinformation["tack_free_time"],
                            "Skinformation": skinformation["skinformation_time"]
                        }
                    })
                    # also include after-storage skinformation results
                    cursor.execute("""
                        SELECT
                            skinformation.tack_free_time,
                            skinformation.skinformation_time,
                            skinformation.test_date,
                            users.name AS operator
                        FROM skinformation
                        JOIN after_storage
                            ON skinformation.afterstorage_id = after_storage.afterstorage_id
                        JOIN users
                            ON users.user_id = skinformation.operator_id
                        WHERE after_storage.sample_id = %s
                    """,
                    (sample_id,)
                    )
                    for s_as in cursor.fetchall():
                        results.append({
                            "test_name": "Skinformation (after storage)",
                            "operator": s_as["operator"],
                            "test_date": format_datetime(s_as["test_date"]),
                            "values": {
                                "Tack free": s_as["tack_free_time"],
                                "Skinformation": s_as["skinformation_time"]
                            }
                        })
                else:
                    cursor.execute("""
                        SELECT
                            skinformation.tack_free_time,
                            skinformation.skinformation_time,
                            skinformation.test_date,
                            users.name AS operator
                        FROM skinformation
                        JOIN after_storage
                            ON skinformation.afterstorage_id = after_storage.afterstorage_id
                        JOIN users
                            ON users.user_id = skinformation.operator_id
                        WHERE after_storage.sample_id = %s
                    """,
                    (sample_id,)
                    )
                    skinformation_as = cursor.fetchone()
                    if skinformation_as:
                        results.append({
                            "test_name": "Skinformation (after storage)",
                            "operator": skinformation_as["operator"],
                            "test_date": format_datetime(skinformation_as["test_date"]),
                            "values": {
                                "Tack free": skinformation_as["tack_free_time"],
                                "Skinformation": skinformation_as["skinformation_time"]
                            }
                        })
                    else:
                        results.append({
                            "test_name": "Skinformation",
                            "operator": "",
                            "test_date": "",
                            "values": {
                                "Status": "No result recorded"
                            }
                        })

            # Density
            if 4 in required_tests:
                cursor.execute("""
                    SELECT
                        ROUND(density.density_product,2)
                        AS density_product,
                        density.test_date,
                        users.name AS operator
                    FROM density
                    JOIN users
                    ON users.user_id = density.operator_id
                    WHERE density.sample_id = %s

                """,
                (sample_id,)
                )
                density = cursor.fetchone()
                if density:

                    results.append({
                        "test_name": "Density",
                        "operator": density["operator"],
                        "test_date": format_datetime(density["test_date"]),

                        "values": {
                            "Density": density["density_product"]
                        }
                    })
                else:
                        results.append({
                            "test_name": "Density",
                            "operator": "",
                            "test_date": "",
                            "values": {
                                "Status": "No result recorded"
                            }
                        })

            # Shore A
            if 3 in required_tests:
                cursor.execute("""
                    SELECT
                        shore_a.shore_a_avg,
                        shore_a.temperature,
                        shore_a.humidity,
                        shore_a.test_date,
                        users.name AS operator
                    FROM shore_a
                    JOIN users
                    ON users.user_id = shore_a.operator_id
                    WHERE shore_a.sample_id = %s

                """,
                (sample_id,)
                )
                shore_a = cursor.fetchone()
                if shore_a:

                    results.append({
                        "test_name": "Shore A",
                        "operator": shore_a["operator"],
                        "test_date": format_datetime(shore_a["test_date"]),

                        "values": {
                            "Average": shore_a["shore_a_avg"],
                            "Temperature": shore_a["temperature"],
                            "Humidity": shore_a["humidity"]
                        }
                    })
                else:
                        results.append({
                            "test_name": "Shore A",
                            "operator": "",
                            "test_date": "",
                            "values": {
                                "Status": "No result recorded"
                            }
                        })
    
            
            # Curability
            if 2 in required_tests:
                cursor.execute("""
                    SELECT
                        curability.day_1,
                        curability.day_7,
                        curability.test_date, 
                        users.name AS operator
                    FROM curability
                    JOIN users
                    ON users.user_id = curability.operator_id
                    WHERE curability.sample_id = %s

                """,
                (sample_id,)
                )
                curability = cursor.fetchone()
                if curability:

                    results.append({
                        "test_name": "Curability",
                        "operator": curability["operator"],
                        "test_date": format_datetime(curability["test_date"]),
                        "values": {
                            "24h": curability["day_1"],
                            "7d": curability["day_7"]
                        }
                    })
                    # also include after-storage curability results
                    cursor.execute("""
                        SELECT
                            curability.day_1,
                            curability.day_7,
                            curability.test_date,
                            users.name AS operator
                        FROM curability
                        JOIN after_storage
                            ON curability.afterstorage_id = after_storage.afterstorage_id
                        JOIN users
                            ON users.user_id = curability.operator_id
                        WHERE after_storage.sample_id = %s
                    """,
                    (sample_id,)
                    )
                    for c_as in cursor.fetchall():
                        results.append({
                            "test_name": "Curability (after storage)",
                            "operator": c_as["operator"],
                            "test_date": format_datetime(c_as["test_date"]),
                            "values": {
                                "24h": c_as["day_1"],
                                "7d": c_as["day_7"]
                            }
                        })
                else:
                    cursor.execute("""
                        SELECT
                            curability.day_1,
                            curability.day_7,
                            curability.test_date,
                            users.name AS operator
                        FROM curability
                        JOIN after_storage
                            ON curability.afterstorage_id = after_storage.afterstorage_id
                        JOIN users
                            ON users.user_id = curability.operator_id
                        WHERE after_storage.sample_id = %s
                    """,
                    (sample_id,)
                    )
                    curability_as = cursor.fetchone()
                    if curability_as:
                        results.append({
                            "test_name": "Curability (after storage)",
                            "operator": curability_as["operator"],
                            "test_date": format_datetime(curability_as["test_date"]),
                            "values": {
                                "24h": curability_as["day_1"],
                                "7d": curability_as["day_7"]
                            }
                        })
                    else:
                        results.append({
                            "test_name": "Curability",
                            "operator": "",
                            "test_date": "",
                            "values": {
                                "Status": "No result recorded"
                            }
                        })

            # Tensile
            if 5 in required_tests:
                cursor.execute("""
                    SELECT
                        ROUND(AVG(tensile_specimen.t_50),3)
                        AS t_50,
                        ROUND(AVG(tensile_specimen.t_100),3)
                        AS t_100,
                        ROUND(AVG(tensile_specimen.t_max),3)
                        AS t_max,
                        ROUND(AVG(tensile_specimen.e_max),3)
                        AS e_max,
                        tensile_strength.test_date, 
                        users.name AS operator
                    FROM tensile_specimen
                    JOIN tensile_strength
                    ON tensile_strength.sample_id =
                    tensile_specimen.sample_id
                    JOIN users
                    ON users.user_id =
                    tensile_strength.operator_id
                    WHERE tensile_specimen.sample_id = %s
                    GROUP BY
                        tensile_strength.test_date,
                        users.name

                """,
                (sample_id,)
                )
                tensile = cursor.fetchone()
                if tensile:

                    results.append({
                        "test_name": "Tensile",
                        "operator": tensile["operator"],
                        "test_date": format_datetime(tensile["test_date"]),

                        "values": {
                            "T50": tensile["t_50"],
                            "T100": tensile["t_100"],
                            "Tmax": tensile["t_max"],
                            "Emax": tensile["e_max"]
                        }
                    })
                else:
                    results.append({
                        "test_name": "Tensile",
                        "operator": "",
                        "test_date": "",
                        "values": {
                            "Status": "No result recorded"
                        }
                    })

            # Adhesion
            if 6 in required_tests:
                cursor.execute("""
                    SELECT
                        adhesion.rubber AS rubber,
                        adhesion.copper AS copper,
                        adhesion.wood AS wood,
                        adhesion.aluminium AS aluminium,
                        adhesion.aluminium_anod AS aluminium_anod,
                        adhesion.lead AS lead,
                        adhesion.rvs AS rvs,
                        adhesion.concrete AS concrete,
                        adhesion.glass AS glass,
                        adhesion.pvc AS pvc,
                        adhesion.pmma AS pmma,
                        adhesion.pc AS pc,
                        adhesion.test_date,
                        users.name AS operator
                    FROM adhesion
                    JOIN users
                    ON users.user_id = adhesion.operator_id
                    WHERE adhesion.sample_id = %s

                """,
                (sample_id,)
                )
                adhesion = cursor.fetchone()
                if adhesion:

                    results.append({
                        "test_name": "Adhesion",
                        "operator": adhesion["operator"],
                        "test_date": format_datetime(adhesion["test_date"]),

                        "values": {
                            "Rubber": adhesion["rubber"],
                            "Copper": adhesion["copper"],
                            "Wood": adhesion["wood"],
                            "Aluminium": adhesion["aluminium"],
                            "Aluminium Anod.": adhesion["aluminium_anod"],
                            "Lead": adhesion["lead"],
                            "RVS": adhesion["rvs"],
                            "Concrete": adhesion["concrete"],
                            "Glass": adhesion["glass"],
                            "PVC": adhesion["pvc"],
                            "PMMA": adhesion["pmma"],
                            "PC": adhesion["pc"]
                        }
                    })
                else:
                        results.append({
                            "test_name": "Adhesion",
                            "operator": "",
                            "test_date": "",
                            "values": {
                                "Status": "No result recorded"
                            }
                        })

            # EPDM Adhesion
            if 7 in required_tests:
                cursor.execute("""
                    SELECT
                        epdm_adhesion.europees AS europees,
                        epdm_adhesion.trc AS trc,
                        epdm_adhesion.carlisle AS carlisle,
                        epdm_adhesion.rubber AS rubber,
                        epdm_adhesion.copper AS copper,
                        epdm_adhesion.wood AS wood,
                        epdm_adhesion.aluminium AS aluminium,
                        epdm_adhesion.aluminium_anod AS aluminium_anod,
                        epdm_adhesion.lead AS lead,
                        epdm_adhesion.rvs AS rvs,
                        epdm_adhesion.concrete AS concrete,
                        epdm_adhesion.glass AS glass,
                        epdm_adhesion.pvc AS pvc,
                        epdm_adhesion.pmma AS pmma,
                        epdm_adhesion.pc AS pc,
                        epdm_adhesion.test_date,
                        users.name AS operator
                    FROM epdm_adhesion
                    JOIN users
                    ON users.user_id = epdm_adhesion.operator_id
                    WHERE epdm_adhesion.sample_id = %s

                """,
                (sample_id,)
                )
                epdm = cursor.fetchone()
                if epdm:

                    results.append({
                        "test_name": "EPDM Adhesion",
                        "operator": epdm["operator"],
                        "test_date": format_datetime(epdm["test_date"]),

                        "values": {
                            "Eu-EPDM": epdm["europees"],
                            "TRC-EPDM": epdm["trc"],
                            "CL-EPDM": epdm["carlisle"],
                            "Rubber": epdm["rubber"],
                            "Copper": epdm["copper"],
                            "Wood": epdm["wood"],
                            "Aluminium": epdm["aluminium"],
                            "Aluminium Anod.": epdm["aluminium_anod"],
                            "Lead": epdm["lead"],
                            "RVS": epdm["rvs"],
                            "Concrete": epdm["concrete"],
                            "Glass": epdm["glass"],
                            "PVC": epdm["pvc"],
                            "PMMA": epdm["pmma"],
                            "PC": epdm["pc"]
                        }
                    })
                else:
                        results.append({
                            "test_name": "EPDM Adhesion",
                            "operator": "",
                            "test_date": "",
                            "values": {
                                "Status": "No result recorded"
                            }
                        })


    cursor.close()
    connection.close()
    return render_template(
        "batch_search.html",
        batch=batch,
        results=results
    )

@app.route("/users")
@login_required
def users():

    return "Users page"

if __name__ == "__main__":
    app.run(debug=True)