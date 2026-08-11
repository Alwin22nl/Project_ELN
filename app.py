import os
from dotenv import load_dotenv
from flask import session, Flask, render_template, request, redirect, url_for, jsonify
from database import get_connection, get_dict_cursor
from helper import log_change
from datetime import date, timedelta, datetime
from numbers import Real
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import secrets
import string

load_dotenv()
today = date.today()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")
app.permanent_session_lifetime = timedelta(hours=1)
app.config["SESSION_REFRESH_EACH_REQUEST"] = True

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

TEST_PAGES = [
    {
        "name": "Rheology",
        "endpoint": "rheology",
    },
    {
        "name": "Skinformation",
        "endpoint": "skinformation",
    },
    {
        "name": "Initial Tack",
        "endpoint": "initial_tack",
    },
    {
        "name": "Density",
        "endpoint": "density",
    },
    {
        "name": "Shore A",
        "endpoint": "shore_a",
    },
    {
        "name": "Adhesion",
        "endpoint": "adhesion",
    },
    {
        "name": "EPDM Adhesion",
        "endpoint": "epdm_adhesion", 
    },

    {
        "name": "Curability",
        "endpoint": "curability", 
    },
    {
        "name": "Tensile Strength",
        "endpoint": "tensile",
    }       
]

OVERVIEW_TESTS = {
    1: {
        "header": "Yield Stress",
        "field": "yield_stress"
    },
    2: {
        "header": "Curability 1d",
        "field": "day_1"
    },
    3: {
        "header": "Shore A",
        "field": "shore_a_avg"
    },
    4: {
        "header": "Density",
        "field": "density_product"
    },
    5: {
        "header": "T-Max",
        "field": "t_max"
    },
    6: {
        "header": "Adhesion",
        "field": "adhesion"
    },
    7: {
        "header": "EPDM Adhesion",
        "field": "epdm_adhesion"
    },
    8: {
        "header": "Initial Tack",
        "field": "initial_tack"
    },
    9: {
        "header": "Skinformation",
        "field": "skinformation_time"
    }
}

# routes
@app.route("/login", methods=["GET","POST"])
def login():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]


        connection = get_connection()
        cursor = get_dict_cursor(connection)

        cursor.execute(
            """
            SELECT *
            FROM users
            WHERE username = %s
            AND active = TRUE
            """,
            (username,)
        )

        user = cursor.fetchone()

        cursor.close()
        connection.close()


        if user and check_password_hash(
            user["password_hash"],
            password
        ):

            session.permanent = True

            session["user_id"] = user["user_id"]
            session["username"] = user["username"]
            session["role"] = user["user_role"]
            session["name"] = user["name"]


            if user["must_change_password"]:
                return redirect(url_for("change_password"))

            else: 
                return redirect(
                url_for("dashboard")
            )


    return render_template(
        "login.html"
    )

@app.route("/logout")
def logout():

    session.clear()

    return redirect(
        url_for("login")
    )

@app.route("/change_password", methods=["GET", "POST"])
@login_required
def change_password():

    if request.method == "POST":
        password1 = request.form["password1"]
        password2 = request.form["password2"]
        if password1 != password2:
            return render_template(
                "change_password.html",
                error="Passwords do not match."
            )
        password_hash = generate_password_hash(password1)
        connection = get_connection()
        cursor = get_dict_cursor(connection)

        cursor.execute(
            """
            UPDATE users
            SET
                password_hash = %s,
                must_change_password = FALSE
            WHERE user_id = %s
            """,
            (
                password_hash,
                session["user_id"]
            )
        )
        connection.commit()
        cursor.close()
        connection.close()
        return redirect(url_for("dashboard"))

    return render_template("change_password.html")

@app.route("/admin")
@login_required
@admin_required
def admin_page():

    connection = get_connection()
    cursor = get_dict_cursor(connection)

    cursor.execute(
        """
        SELECT
            user_id,
            username,
            name,
            user_role,
            active
        FROM users
        ORDER BY username
        """
    )

    users = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template(
        "admin/admin.html",
        users=users
    )

@app.route("/admin/audit_logs")
@login_required
@admin_required
def audit_logs_admin():
    if session.get("role") != "admin":
        return "Access denied", 403
    connection = get_connection()
    cursor = get_dict_cursor(connection)
    cursor.execute("""
        SELECT
            audit_log.audit_id,
            audit_log.table_name,
            audit_log.record_id,
            audit_log.changed_at,
            audit_log.old_values,
            audit_log.new_values,
            audit_log.reason,
            users.username
        FROM audit_log
        JOIN users
        ON users.user_id = audit_log.changed_by
        ORDER BY audit_log.changed_at DESC
    """)
    logs = cursor.fetchall()

    cursor.close()
    connection.close()
    return render_template(
        "admin/audit_logs.html",
        logs=logs
    )

@app.route("/admin/reset_password/<int:user_id>", methods=["POST"])
@login_required
@admin_required
def reset_password(user_id):

    temp_password = generate_temp_password()
    password_hash = generate_password_hash(
        temp_password
    )
    connection = get_connection()
    cursor = get_dict_cursor(connection)
    cursor.execute(
        """
        UPDATE users
        SET
            password_hash = %s,
            must_change_password = TRUE
        WHERE user_id = %s
        """,
        (
            password_hash,
            user_id
        )
    )
    connection.commit()
    cursor.close()
    connection.close()

    return render_template(
        "admin/password_reset.html",
        password=temp_password
    )

@app.route("/admin/create_user", methods=["GET","POST"])
@login_required
@admin_required
def create_user():

    if request.method == "POST":

        username = request.form["username"]
        name = request.form["name"]
        role = request.form["user_role"]

        # temporary password
        temp_password = generate_temp_password()
        password_hash = generate_password_hash(
            temp_password
        )
        connection = get_connection()
        cursor = get_dict_cursor(connection)
        cursor.execute(
            """
            INSERT INTO users
            (
                username,
                name,
                password_hash,
                user_role,
                must_change_password,
                active
            )
            VALUES
            (%s,%s,%s,%s,TRUE,TRUE)
            """,
            (
                username,
                name,
                password_hash,
                role
            )
        )
        connection.commit()
        cursor.close()
        connection.close()
        return render_template(
            "admin/user_created.html",
            username=username,
            password=temp_password
        )

    return render_template(
        "admin/create_user.html"
    )

@app.route("/")
@login_required
def dashboard():
    connection = get_connection()
    cursor = get_dict_cursor(connection)
    
    # Curability removal schedule
    cursor.execute("""
        SELECT *
        FROM (
            SELECT
                samples.sample_id,
                samples.batch_nr,
                products.product_name,
                samples.prod_date,
                CASE
                    WHEN curability_preparation.removed_24h_at IS NULL
                        THEN 'Remove 24h sample'
                    WHEN curability_preparation.removed_7d_at IS NULL
                        THEN 'Remove 7d sample'
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
    """)

    curability_schedule = cursor.fetchall()

    #After Storage Prep
    cursor.execute("""
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
                AND a.placed_in_oven_at + INTERVAL '28 days'
                    <= NOW()
        ) AS after_storage_schedule
        ORDER BY due_date;
    """)

    after_storage_schedule = cursor.fetchall()


    #Rheology
    cursor.execute("""
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
        ORDER BY prod_date;
    """)

    rheology = cursor.fetchall()

    #skinformation
    cursor.execute("""
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
        ORDER BY prod_date;
    """)
    
    skinformation = cursor.fetchall()

    #Initial Tack
    cursor.execute("""
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
        ORDER BY samples.prod_date
    """)
    
    initial_tack = cursor.fetchall()

    #Tensile
    cursor.execute("""
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
                        THEN 'Prepare'
                    WHEN tensile_prep.prepared_date > CURRENT_DATE - INTERVAL '7 days'
                        THEN NULL
                    WHEN NOT EXISTS (
                        SELECT 1
                        FROM tensile_specimen ts
                        WHERE ts.sample_id = samples.sample_id
                        )
                        THEN 'Measure'
                    WHEN tensile_strength.sample_id IS NULL
                        THEN 'Test'
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
        ORDER BY prod_date
    """)

    tensile = cursor.fetchall()

    #Shore A
    cursor.execute("""
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
                        THEN 'Prepare'
                    WHEN shore_a_prep.prepared_date > CURRENT_DATE - INTERVAL '7 days'
                        THEN NULL
                    WHEN shore_a.sample_id IS NULL
                        THEN 'Test'
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
        ORDER BY prod_date
    """)

    shore_a = cursor.fetchall()

    #Adhesion
    cursor.execute("""
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
                        THEN 'Prepare'
                    WHEN adhesion_prep.prepared_date > CURRENT_DATE - INTERVAL '7 days'
                        THEN NULL
                    WHEN adhesion.sample_id IS NULL
                        THEN 'Test'
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
        ORDER BY prod_date
    """)

    adhesion = cursor.fetchall()
    
    #EPDM Adhesion
    cursor.execute("""
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
                        THEN 'Prepare'
                    WHEN epdm_adhesion_prep.prepared_date > CURRENT_DATE - INTERVAL '7 days'
                        THEN NULL
                    WHEN epdm_adhesion.sample_id IS NULL
                        THEN 'Test'
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
        ORDER BY prod_date
    """)
    epdm_adhesion = cursor.fetchall()

    # Curabillity
    cursor.execute("""
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
                        THEN 'Prepare'
                    WHEN curability_preparation.removed_24h_at IS NOT NULL
                    AND curability_preparation.removed_7d_at IS NOT NULL
                    AND (
                        curability.day_1 IS NULL
                        OR curability.day_7 IS NULL
                    )
                        THEN 'Measure'
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
                            THEN 'Prepare'
                        WHEN curability_prep.removed_24h_at IS NOT NULL
                        AND curability_prep.removed_7d_at IS NOT NULL
                        AND (
                            curability.day_1 IS NULL
                            OR curability.day_7 IS NULL
                        )
                            THEN 'Measure'
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
        ORDER BY prod_date;
        """)
    curability = cursor.fetchall()

    #Density
    cursor.execute("""
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
        ORDER BY samples.prod_date
        """)

    density = cursor.fetchall()

    return render_template(
        "home.html",
        rheology=rheology,
        initial_tack=initial_tack,
        skinformation=skinformation,
        shore_a =shore_a,
        tensile=tensile,
        adhesion=adhesion,
        epdm_adhesion=epdm_adhesion,
        curability_schedule=curability_schedule,
        curability=curability,
        density=density,
        after_storage_schedule=after_storage_schedule
    )

@app.route("/afterstorage/place", methods=["POST"])
@login_required
def place_afterstorage():

    sample_id = request.form["sample_id"]
    oven_location = request.form["oven_location"]
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute("""
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
    ))
    connection.commit()
    cursor.close()
    connection.close()
    return redirect(url_for("dashboard"))

@app.route("/afterstorage/remove", methods=["POST"])
@login_required
def remove_afterstorage():

    afterstorage_id = request.form["afterstorage_id"]
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute("""
        UPDATE after_storage
        SET removed_from_oven = NOW()
        WHERE afterstorage_id = %s
    """,
    (afterstorage_id,))
    connection.commit()
    cursor.close()
    connection.close()
    return redirect(url_for("dashboard"))

@app.route("/sample", methods=["GET", "POST"])
@login_required
def sample():

    error = None

    if request.method == "POST":

        batch_nr = request.form["batch_nr"]
        prod_date = request.form["prod_date"]
        product_id = request.form["product_id"]
        after_storage_required = (request.form.get("after_storage_required") == "true")
        remark = request.form["remark"]

        connection = get_connection()
        cursor = get_dict_cursor(connection)

        cursor.execute(
            """
            SELECT COUNT(*) AS count
            FROM samples
            WHERE batch_nr = %s
            """,
            (batch_nr,)
        )

        if cursor.fetchone()["count"] > 0:
            error = f"Batch number '{batch_nr}' already exists."
        else:
            cursor.execute(
            """
            SELECT
                COALESCE(MAX(batch_sequence),0)+1 AS next_sequence
            FROM samples
            WHERE product_id = %s
            """,
            (product_id,)
            )

            next_sequence = cursor.fetchone()["next_sequence"]

            cursor.execute(
                """
                INSERT INTO samples
                (
                    batch_nr,
                    prod_date,
                    product_id,
                    batch_sequence,
                    after_storage_required,
                    remark
                )
                VALUES (%s, %s, %s, %s, %s, %s)
                """,
                (
                    batch_nr,
                    prod_date,
                    product_id,
                    next_sequence,
                    after_storage_required,
                    remark
                )
            )

            connection.commit()
            print("Sample saved!")

        cursor.close()
        connection.close()

    connection = get_connection()
    cursor = get_dict_cursor(connection)

    cursor.execute("""
        SELECT product_id, product_name
        FROM products
        ORDER BY product_name
    """)

    products = cursor.fetchall()

    cursor.execute("""
        SELECT
            samples.sample_id,
            samples.batch_nr,
            products.product_name,
            samples.prod_date,
            samples.product_id
        FROM samples
        JOIN products
        ON products.product_id = samples.product_id
        ORDER BY samples.sample_id DESC
        LIMIT 30;
    """)

    samples = cursor.fetchall()
    sample_ids = [sample["sample_id"] for sample in samples]
    product_ids = list({sample["product_id"] for sample in samples})

    cursor.execute(
        """
        SELECT
            product_id,
            test_type_id
        FROM product_test_requirements
        WHERE product_id = ANY(%s)
        """,
        (product_ids,)
    )
    requirements = cursor.fetchall()
    required_tests = {}
    for row in requirements:
        required_tests.setdefault(row["product_id"], set()).add(row["test_type_id"])

    cursor.execute(
        """
        SELECT
            afterstorage_id,
            sample_id
        FROM after_storage
        WHERE sample_id = ANY(%s)
        """,
        (sample_ids,)
    )
    after_storage_rows = cursor.fetchall()
    afterstorage_by_sample = {}
    afterstorage_ids = []
    for row in after_storage_rows:
        afterstorage_by_sample.setdefault(row["sample_id"], []).append(row["afterstorage_id"])
        afterstorage_ids.append(row["afterstorage_id"])

    cursor.execute(
        """
        SELECT sample_id
        FROM initial_tack
        WHERE sample_id = ANY(%s)
        """,
        (sample_ids,)
    )
    initial_tack_done = {row["sample_id"] for row in cursor.fetchall()}

    cursor.execute(
        """
        SELECT sample_id
        FROM density
        WHERE sample_id = ANY(%s)
        """,
        (sample_ids,)
    )
    density_done = {row["sample_id"] for row in cursor.fetchall()}

    cursor.execute(
        """
        SELECT sample_id
        FROM shore_a
        WHERE sample_id = ANY(%s)
        """,
        (sample_ids,)
    )
    shore_a_done = {row["sample_id"] for row in cursor.fetchall()}

    cursor.execute(
        """
        SELECT sample_id
        FROM adhesion
        WHERE sample_id = ANY(%s)
        """,
        (sample_ids,)
    )
    adhesion_done = {row["sample_id"] for row in cursor.fetchall()}

    cursor.execute(
        """
        SELECT sample_id
        FROM epdm_adhesion
        WHERE sample_id = ANY(%s)
        """,
        (sample_ids,)
    )
    epdm_adhesion_done = {row["sample_id"] for row in cursor.fetchall()}

    cursor.execute(
        """
        SELECT sample_id
        FROM tensile_strength
        WHERE sample_id = ANY(%s)
        """,
        (sample_ids,)
    )
    tensile_done = {row["sample_id"] for row in cursor.fetchall()}

    cursor.execute(
        """
        SELECT sample_id
        FROM curability
        WHERE sample_id = ANY(%s)
        """,
        (sample_ids,)
    )
    curability_sample_done = {row["sample_id"] for row in cursor.fetchall()}

    curability_afterstorage_done = set()
    if afterstorage_ids:
        cursor.execute(
            """
            SELECT a.sample_id
            FROM curability c
            JOIN after_storage a
            ON c.afterstorage_id = a.afterstorage_id
            WHERE a.afterstorage_id = ANY(%s)
            """,
            (afterstorage_ids,)
        )
        curability_afterstorage_done = {row["sample_id"] for row in cursor.fetchall()}

    rheology_sample_done = set()
    rheology_afterstorage_done = set()
    cursor.execute(
        """
        SELECT sample_id
        FROM rheology
        WHERE sample_id = ANY(%s)
        """,
        (sample_ids,)
    )
    rheology_sample_done = {row["sample_id"] for row in cursor.fetchall()}

    if afterstorage_ids:
        cursor.execute(
            """
            SELECT a.sample_id
            FROM rheology r
            JOIN after_storage a
            ON r.afterstorage_id = a.afterstorage_id
            WHERE a.afterstorage_id = ANY(%s)
            """,
            (afterstorage_ids,)
        )
        rheology_afterstorage_done = {row["sample_id"] for row in cursor.fetchall()}

    skinformation_sample_done = set()
    skinformation_afterstorage_done = set()
    cursor.execute(
        """
        SELECT sample_id
        FROM skinformation
        WHERE sample_id = ANY(%s)
        """,
        (sample_ids,)
    )
    skinformation_sample_done = {row["sample_id"] for row in cursor.fetchall()}

    if afterstorage_ids:
        cursor.execute(
            """
            SELECT a.sample_id
            FROM skinformation s
            JOIN after_storage a
            ON s.afterstorage_id = a.afterstorage_id
            WHERE a.afterstorage_id = ANY(%s)
            """,
            (afterstorage_ids,)
        )
        skinformation_afterstorage_done = {row["sample_id"] for row in cursor.fetchall()}

    sample_list = []

    for sample in samples:
        due_date = sample["prod_date"] + timedelta(days=7)
        product_id = sample["product_id"]
        requirement_set = required_tests.get(product_id, set())

        def test_done(sample_id, test_type):
            if test_type == 1:
                return (
                    sample_id in rheology_sample_done
                    or sample_id in rheology_afterstorage_done
                )
            if test_type == 2:
                return (
                    sample_id in curability_sample_done
                    or sample_id in curability_afterstorage_done
                )
            if test_type == 3:
                return sample_id in shore_a_done
            if test_type == 4:
                return sample_id in density_done
            if test_type == 5:
                return sample_id in tensile_done
            if test_type == 6:
                return sample_id in adhesion_done
            if test_type == 7:
                return sample_id in epdm_adhesion_done
            if test_type == 8:
                return sample_id in initial_tack_done
            if test_type == 9:
                return (
                    sample_id in skinformation_sample_done
                    or sample_id in skinformation_afterstorage_done
                )
            return False

        completed = all(test_done(sample["sample_id"], test_type)
                        for test_type in requirement_set)

        if completed:
            status = "🟢 Completed"
        elif today < due_date:
            status = "🔴 Wait with Testing"
        else:
            status = "🟠 Available for Testing / in progress"

        sample_list.append({
            "batch_nr": sample["batch_nr"],
            "product": sample["product_name"],
            "prod_date": sample["prod_date"],
            "due_date": due_date,
            "status": status
        })
    cursor.close()
    connection.close()

    return render_template(
        "sample.html",
        products=products,
        samples=sample_list,
        error=error
    )

@app.route("/tests")
@login_required
def tests():

    return render_template(
        "tests.html",
        tests=TEST_PAGES
    )

# test routes
@app.route("/test/rheology", methods=["GET", "POST"])
@login_required
def rheology():

    connection = get_connection()
    cursor = get_dict_cursor(connection)
    if request.method == "POST":
        cursor.execute(
            """
            INSERT INTO rheology
            (
                sample_id,
                afterstorage_id
                operator_id,
                remark,
                yield_stress,
                vis_at_1,
                vis_at_5,
                vis_at_10,
                humidity
            )
            VALUES
            (%s,%s,%s,%s,%s,%s,%s,%s)
            """,
            (
                request.form["sample_id"],
                request.form.get("afterstorage_id") or None,
                session["user_id"],
                request.form["remark"],
                request.form["yield_stress"],
                request.form["vis_at_1"],
                request.form["vis_at_5"],
                request.form["vis_at_10"],
                request.form["humidity"]
            )
        )
        connection.commit()
        cursor.close()
        connection.close()
        return redirect(url_for("rheology"))

    # GET: Load products requiring rheology
    cursor.execute(
        """
        SELECT
            products.product_id,
            products.product_name
        FROM products
        JOIN product_test_requirements
        ON product_test_requirements.product_id =
           products.product_id
        WHERE product_test_requirements.test_type_id = 1
        ORDER BY products.product_name
        """
    )
    products = cursor.fetchall()
    # Load latest results
    cursor.execute(
        """
        SELECT
            samples.batch_nr,
            rheology.yield_stress,
            rheology.vis_at_1,
            rheology.vis_at_5,
            rheology.vis_at_10,
            rheology.humidity
        FROM rheology
        JOIN samples
        ON samples.sample_id = rheology.sample_id
        ORDER BY rheology.rheology_id DESC
        LIMIT 25
        """
    )
    results = cursor.fetchall()
    cursor.close()
    connection.close()
    return render_template(
        "tests/rheology.html",
        products=products,
        results=results
    )

@app.route("/get_rheology_samples/<int:product_id>")
@login_required
def get_rheology_samples(product_id):

    connection = get_connection()
    cursor = get_dict_cursor(connection)

    cursor.execute(
        """
        SELECT
            samples.sample_id,
            NULL::INTEGER AS afterstorage_id,
            samples.batch_nr AS display_name
        FROM samples
        LEFT JOIN rheology
        ON rheology.sample_id = samples.sample_id
        WHERE samples.product_id = %s
        AND samples.prod_date <= CURRENT_DATE - 7
        AND MOD(
            samples.batch_sequence,
            (
                SELECT frequency
                FROM product_test_requirements
                WHERE product_id = samples.product_id
                AND test_type_id = 1
            )
        ) = 0
        AND rheology.sample_id IS NULL
        UNION ALL
        SELECT
            samples.sample_id,
            after_storage.afterstorage_id,
            samples.batch_nr || ' AS' AS display_name
        FROM after_storage
        JOIN samples
        ON samples.sample_id = after_storage.sample_id
        LEFT JOIN rheology
        ON rheology.afterstorage_id = after_storage.afterstorage_id
        WHERE 
            samples.product_id = %s
            AND after_storage.removed_from_oven IS NOT NULL
            AND rheology.afterstorage_id IS NULL
        ORDER BY sample_id
        """,
        (product_id, product_id)
    )

    samples = cursor.fetchall()
    cursor.close()
    connection.close()

    return {
        "samples": [
            {
                "sample_id": sample["sample_id"],
                "afterstorage_id": sample["afterstorage_id"],
                "display_name": sample["display_name"]
            }
            for sample in samples
        ]
    }

@app.route("/test/skinformation", methods=["GET","POST"])
def skinformation():

    connection = get_connection()
    cursor = get_dict_cursor(connection)

    if request.method == "POST":
        sample_ids = request.form.getlist("sample_id[]")
        tack_times = request.form.getlist("tack_free_time[]")
        tack_temps = request.form.getlist("temp_tack_free_time[]")
        tack_rhs = request.form.getlist("rh_tack_free_time[]")
        skin_times = request.form.getlist("skinformation_time[]")
        skin_temps = request.form.getlist("temp_skinformation_time[]")
        skin_rhs = request.form.getlist("rh_skinformation_time[]")
        remarks = request.form.getlist("remark[]")
        operator_id = session["user_id"]
        afterstorage_id = request.form.get("afterstorage_id[]") or None

        for i in range(len(sample_ids)):
            if sample_ids[i] == "":
                continue

            cursor.execute(
                """
                INSERT INTO skinformation
                (
                    sample_id,
                    operator_id,
                    afterstorage_id,
                    remark,
                    tack_free_time,
                    temp_tack_free_time,
                    rh_tack_free_time,
                    skinformation_time,
                    temp_skinformation_time,
                    rh_skinformation_time
                )
                VALUES
                (%s,%s,%s,%s,%s,%s,%s,%s,%s, %s)
                """,
                (
                    sample_ids[i],
                    operator_id,
                    afterstorage_id[i],
                    remarks[i],
                    tack_times[i],
                    tack_temps[i],
                    tack_rhs[i],
                    skin_times[i],
                    skin_temps[i],
                    skin_rhs[i]
                )
            )
        connection.commit()
        return redirect(url_for("skinformation"))

    cursor.execute(
    """
        SELECT
            samples.sample_id,
            NULL::INTEGER AS afterstorage_id,
            samples.batch_nr AS display_name,
            products.product_name
        FROM samples
        JOIN products
        ON products.product_id = samples.product_id
        JOIN product_test_requirements
        ON product_test_requirements.product_id = products.product_id
        LEFT JOIN skinformation
        ON skinformation.sample_id = samples.sample_id
        WHERE
            product_test_requirements.test_type_id = 9
        AND skinformation.sample_id IS NULL
        AND MOD(
            samples.batch_sequence,
            product_test_requirements.frequency
        ) = 0
        UNION ALL
        SELECT
            samples.sample_id,
            after_storage.afterstorage_id,
            samples.batch_nr || ' AS' AS display_name,
            products.product_name
        FROM after_storage
        JOIN samples
        ON samples.sample_id = after_storage.sample_id
        LEFT JOIN skinformation
        ON skinformation.afterstorage_id = after_storage.afterstorage_id
        JOIN products 
        ON products.product_id = samples.product_id
        WHERE after_storage.removed_from_oven IS NOT NULL
            AND skinformation.afterstorage_id IS NULL
        ORDER BY sample_id
         """)   

    samples = cursor.fetchall()
    samples = [
        {
            "sample_id": sample["sample_id"],
            "afterstorage_id": sample["afterstorage_id"],
            "display_name": sample["display_name"]
        }
        for sample in samples
    ]

    return render_template(
    "tests/skinformation.html",
    products=products,
    samples=samples
    )

@app.route("/test/initial_tack", methods=["GET", "POST"])
@login_required
def initial_tack():

    connection = get_connection()
    cursor = get_dict_cursor(connection)
    if request.method == "POST":
        sample_id = request.form["sample_id"]
        operator_id = session["user_id"]
        remark = request.form["remark"]
        area = float(request.form["area"])
        area_weight = float(request.form["area_weight"])
        added_weight = float(request.form["added_weight"])
        humidity = request.form["humidity"]
        initial_tack = (area_weight + added_weight) / area

        cursor.execute(
            """
            INSERT INTO initial_tack
            (
                sample_id,
                operator_id,
                remark,
                area,
                area_weight,
                added_weight,
                humidity,
                initial_tack
            )
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
            """,
            (
                sample_id,
                operator_id,
                remark,
                area,
                area_weight,
                added_weight,
                humidity,
                initial_tack
            )
        )
        connection.commit()
        cursor.close()
        connection.close()
        return redirect(url_for("initial_tack"))

    # GET: Load products requiring initial_tack
    cursor.execute(
        """
        SELECT
            products.product_id,
            products.product_name
        FROM products
        JOIN product_test_requirements
        ON product_test_requirements.product_id =
           products.product_id
        WHERE product_test_requirements.test_type_id = 8
        ORDER BY products.product_name
        """
    )
    products = cursor.fetchall()
    # Load latest results
    cursor.execute(
        """
        SELECT
            samples.batch_nr,
            initial_tack.area,
            initial_tack.area_weight,
            initial_tack.added_weight,
            initial_tack.initial_tack,
            initial_tack.humidity
        FROM initial_tack
        JOIN samples
        ON samples.sample_id = initial_tack.sample_id
        ORDER BY initial_tack.initial_tack_id DESC
        LIMIT 25
        """
    )
    results = cursor.fetchall()
    cursor.close()
    connection.close()
    return render_template(
        "tests/initial_tack.html",
        products=products,
        results=results
    )

@app.route("/get_initial_tack_samples/<int:product_id>")
def get_initial_tack_samples(product_id):

    connection = get_connection()
    cursor = get_dict_cursor(connection)

    cursor.execute(
        """
        SELECT
            samples.sample_id,
            samples.batch_nr
        FROM samples
        LEFT JOIN initial_tack
        ON initial_tack.sample_id = samples.sample_id
        WHERE samples.product_id = %s
        AND samples.prod_date <= CURRENT_DATE - 7
        AND MOD(
            samples.batch_sequence,
            (
                SELECT frequency
                FROM product_test_requirements
                WHERE product_id = samples.product_id
                AND test_type_id = 8
            )
        ) = 0
        AND initial_tack.sample_id IS NULL
        ORDER BY samples.sample_id
        """,
        (product_id,)
    )

    samples = cursor.fetchall()
    cursor.close()
    connection.close()

    return {
        "samples": [
            {
                "id": sample["sample_id"],
                "batch_nr": sample["batch_nr"]
            }
            for sample in samples
        ]
    }

@app.route("/test/density", methods=["GET", "POST"])
@login_required
def density():

    connection = get_connection()
    cursor = get_dict_cursor(connection)
    if request.method == "POST":
        action = request.form.get("action")
        if action == "correct":
            density_id = request.form["density_id"]
            new_value = float(
                request.form["density_product"]
            )
            reason = request.form["reason"]
            # Get current value
            cursor.execute("""
                SELECT
                    density_product
                FROM density
                WHERE density_id = %s
            """,
            (density_id,)
            )

            old = cursor.fetchone()
            old_values = {
                "density_product": old["density_product"]
            }
            new_values = {
                "density_product": new_value
            }
            # Update result
            cursor.execute("""
                UPDATE density
                SET density_product = %s
                WHERE density_id = %s
            """,
            (
                new_value,
                density_id
            ))
            # Audit trail
            log_change(
                cursor,
                "density",
                density_id,
                old_values,
                new_values,
                reason
            )
            connection.commit()
            cursor.close()
            connection.close()
            return redirect(url_for("density"))

        else:

            sample_id = request.form["sample_id"]
            operator_id = session["user_id"]
            remark = request.form["remark"]
            vessel_empty = float(
                request.form["vessel_empty"]
            )
            vessel_full = float(
                request.form["vessel_full"]
            )
            vessel_volume = float(
                request.form["vessel_volume"]
            )
            density_product = (
                vessel_full - vessel_empty
            ) / vessel_volume

            cursor.execute(
                """
                INSERT INTO density
                (
                    sample_id,
                    operator_id,
                    remark,
                    vessel_empty,
                    vessel_full,
                    vessel_volume,
                    density_product
                )
                VALUES (%s,%s,%s,%s,%s,%s,%s)
                """,
                (
                    sample_id,
                    operator_id,
                    remark,
                    vessel_empty,
                    vessel_full,
                    vessel_volume,
                    density_product
                )
            )

            connection.commit()
            cursor.close()
            connection.close()
            return redirect(url_for("density"))


    # Load products requiring density
    cursor.execute(
        """
        SELECT
            products.product_id,
            products.product_name
        FROM products
        JOIN product_test_requirements
        ON product_test_requirements.product_id =
           products.product_id
        WHERE product_test_requirements.test_type_id = 4
        ORDER BY products.product_name
        """
    )
    products = cursor.fetchall()
    # Load latest results
    cursor.execute(
        """
        SELECT
            density.density_id,
            samples.batch_nr,
            density.vessel_empty,
            density.vessel_full,
            density.vessel_volume,
            density.density_product,
            density.remark
        FROM density
        JOIN samples
        ON samples.sample_id = density.sample_id
        ORDER BY density.density_id DESC
        LIMIT 25
        """
    )
    results = cursor.fetchall()
    cursor.close()
    connection.close()
    return render_template(
        "tests/density.html",
        products=products,
        results=results
    )

@app.route("/get_density_samples/<int:product_id>")
def get_density_samples(product_id):

    connection = get_connection()
    cursor = get_dict_cursor(connection)

    cursor.execute(
        """
        SELECT
            samples.sample_id,
            samples.batch_nr
        FROM samples
        LEFT JOIN density
        ON density.sample_id = samples.sample_id
        WHERE samples.product_id = %s
        AND samples.prod_date <= CURRENT_DATE - 7
        AND samples.batch_sequence = 1
            OR
            MOD(
            samples.batch_sequence,
            (
                SELECT frequency
                FROM product_test_requirements
                WHERE product_id = samples.product_id
                AND test_type_id = 4
            )
        ) = 0
        AND density.sample_id IS NULL
        ORDER BY samples.sample_id
        """,
        (product_id,)
    )

    samples = cursor.fetchall()
    cursor.close()
    connection.close()

    return {
        "samples": [
            {
                "id": sample["sample_id"],
                "batch_nr": sample["batch_nr"]
            }
            for sample in samples
        ]
    }

@app.route("/test/shore_a")
@login_required
def shore_a():

    return render_template("tests/Shore_a/shore_a.html")

@app.route("/test/shore_a/prep", methods=["GET","POST"])
@login_required
def shore_a_prep():

    connection = get_connection()
    cursor = get_dict_cursor(connection)

    if request.method == "POST":
        cursor.execute(
            """
            INSERT INTO shore_a_preparation
            (
                sample_id,
                operator_id,
                remark
            )
            VALUES
            (%s,%s,%s)
            """,
            (
                request.form["sample_id"],
                session["user_id"],
                request.form["remark"]
            )
        )
        connection.commit()
        cursor.close()
        connection.close()
        return redirect(url_for("shore_a_prep"))
    
    
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
            LEFT JOIN shore_a_preparation
            ON shore_a_preparation.sample_id =
            samples.sample_id
            WHERE
                product_test_requirements.test_type_id = 3
            AND shore_a_preparation.sample_id IS NULL
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
            """
    )   

    samples = cursor.fetchall()
    cursor.execute(
        """
        SELECT
            samples.batch_nr,
            products.product_name,
            shore_a_preparation.prepared_date
        FROM shore_a_preparation
        JOIN samples
        ON samples.sample_id =
           shore_a_preparation.sample_id
        JOIN products
        ON products.product_id =
           samples.product_id
        LEFT JOIN shore_a
        ON shore_a.sample_id =
           samples.sample_id
        WHERE shore_a.sample_id IS NULL
        ORDER BY prepared_date DESC
        """
    )

    prepared = cursor.fetchall()
    cursor.close()
    connection.close()

    return render_template(
        "tests/Shore_a/shore_a_prep.html",
        samples=samples,
        prepared=prepared,
        today=date.today()
    )

@app.route("/test/shore_a/test", methods=["GET","POST"])
@login_required
def shore_a_test():

    connection = get_connection()
    cursor = get_dict_cursor(connection)

    # Save new Shore A result

    if request.method == "POST":
        shore_1 = float(request.form["shore_a_1"])
        shore_2 = float(request.form["shore_a_2"])
        shore_3 = float(request.form["shore_a_3"])
        shore_avg = round((shore_1 + shore_2 + shore_3) / 3)
        cursor.execute(
            """
            INSERT INTO shore_a
            (
                sample_id,
                operator_id,
                remark,
                shore_a_1,
                shore_a_2,
                shore_a_3,
                shore_a_avg,
                temperature,
                humidity
            )
            VALUES
            (%s,%s,%s,%s,%s,%s,%s,%s,%s)
            """,
            (
                request.form["sample_id"],
                session["user_id"],
                request.form["remark"],
                shore_1,
                shore_2,
                shore_3,
                shore_avg,
                request.form["temperature"],
                request.form["humidity"]
            )
        )
        connection.commit()
        cursor.close()
        connection.close()
        return redirect(url_for("shore_a_test"))

    # Products requiring Shore A testing
    cursor.execute(
        """
        SELECT
            products.product_id,
            products.product_name
        FROM products
        JOIN product_test_requirements
        ON product_test_requirements.product_id = products.product_id
        WHERE product_test_requirements.test_type_id = 3
        ORDER BY products.product_name
        """
    )
    products = cursor.fetchall()

    # Latest Shore A results
    cursor.execute(
        """
        SELECT
            samples.batch_nr,
            shore_a.shore_a_1,
            shore_a.shore_a_2,
            shore_a.shore_a_3,
            shore_a.shore_a_avg,
            shore_a.temperature,
            shore_a.humidity
        FROM shore_a
        JOIN samples
        ON samples.sample_id = shore_a.sample_id
        ORDER BY shore_a.shore_a_id DESC
        LIMIT 25
        """
    )
    results = cursor.fetchall()
    cursor.close()
    connection.close()
    return render_template(
        "tests/Shore_a/shore_a_test.html",
        products=products,
        results=results
    )

@app.route("/get_shore_a_samples/<int:product_id>")
def get_shore_a_samples(product_id):

    connection = get_connection()
    cursor = get_dict_cursor(connection)
    cursor.execute(
        """
        SELECT
            samples.sample_id,
            samples.batch_nr

        FROM shore_a_preparation
        JOIN samples
        ON samples.sample_id = shore_a_preparation.sample_id
        LEFT JOIN shore_a
        ON shore_a.sample_id = samples.sample_id
        WHERE samples.product_id = %s
        AND shore_a.sample_id IS NULL
        AND shore_a_preparation.prepared_date::date
            <= CURRENT_DATE - INTERVAL '7 days'

        ORDER BY samples.sample_id
        """,
        (product_id,)
    )
    samples = cursor.fetchall()
    cursor.close()
    connection.close()
    return {
    "samples": [
        {
            "id": sample["sample_id"],
            "batch_nr": sample["batch_nr"]
        }
        for sample in samples
    ]
    }

@app.route("/test/adhesion")
@login_required
def adhesion():

    return render_template("tests/adhesion/adhesion.html")

@app.route("/test/adhesion/prep", methods=["GET","POST"])
@login_required
def adhesion_prep():

    connection = get_connection()
    cursor = get_dict_cursor(connection)

    if request.method == "POST":
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
                request.form["sample_id"],
                session["user_id"],
                request.form["remark"]
            )
        )
        connection.commit()
        cursor.close()
        connection.close()
        return redirect(url_for("adhesion_prep"))
    
    
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
            LEFT JOIN adhesion_preparation
            ON adhesion_preparation.sample_id =
            samples.sample_id
            WHERE
                product_test_requirements.test_type_id = 6
            AND adhesion_preparation.sample_id IS NULL
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
            """
    )   

    samples = cursor.fetchall()
    cursor.execute(
        """
        SELECT
            samples.batch_nr,
            products.product_name,
            adhesion_preparation.prepared_date
        FROM adhesion_preparation
        JOIN samples
        ON samples.sample_id =
           adhesion_preparation.sample_id
        JOIN products
        ON products.product_id =
           samples.product_id
        LEFT JOIN adhesion
        ON adhesion.sample_id =
           samples.sample_id
        WHERE adhesion.sample_id IS NULL
        ORDER BY prepared_date DESC
        """
    )

    prepared = cursor.fetchall()
    cursor.close()
    connection.close()

    return render_template(
        "tests/adhesion/adhesion_prep.html",
        samples=samples,
        prepared=prepared,
        today=date.today()
    )

@app.route("/test/adhesion/test", methods=["GET","POST"])
@login_required
def adhesion_test():

    connection = get_connection()
    cursor = get_dict_cursor(connection)

    # Save new adhesion result

    if request.method == "POST":
 
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
                request.form["sample_id"],
                session["user_id"],    
                request.form["remark"],
                request.form["rubber"],
                request.form["copper"],
                request.form["wood"],
                request.form["aluminium"],
                request.form["aluminium_anod"],
                request.form["lead"],
                request.form["rvs"],
                request.form["concrete"],
                request.form["glass"],
                request.form["pvc"],
                request.form["pmma"],
                request.form["pc"]
            )
        )
        connection.commit()
        cursor.close()
        connection.close()
        return redirect(url_for("adhesion_test"))

    # Products requiring adhesion testing
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
    products = cursor.fetchall()

    # Latest Adhesion results
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
        LIMIT 25
        """
    )
    results = cursor.fetchall()
    cursor.close()
    connection.close()
    return render_template(
        "tests/adhesion/adhesion_test.html",
        products=products,
        results=results
    )

@app.route("/get_adhesion_samples/<int:product_id>")
def get_adhesion_samples(product_id):

    connection = get_connection()
    cursor = get_dict_cursor(connection)
    cursor.execute(
        """
        SELECT
            samples.sample_id,
            samples.batch_nr

        FROM adhesion_preparation
        JOIN samples
        ON samples.sample_id = adhesion_preparation.sample_id
        LEFT JOIN adhesion
        ON adhesion.sample_id = samples.sample_id
        WHERE samples.product_id = %s
        AND adhesion.sample_id IS NULL
        AND adhesion_preparation.prepared_date::date
            <= CURRENT_DATE - INTERVAL '7 days'

        ORDER BY samples.sample_id
        """,
        (product_id,)
    )
    samples = cursor.fetchall()
    cursor.close()
    connection.close()
    return {
    "samples": [
        {
            "id": sample["sample_id"],
            "batch_nr": sample["batch_nr"]
        }
        for sample in samples
    ]
    }

@app.route("/test/epdm_adhesion")
@login_required
def epdm_adhesion():

    return render_template("tests/epdm_adhesion/epdm_adhesion.html")

@app.route("/test/epdm_adhesion/prep", methods=["GET","POST"])
@login_required
def epdm_adhesion_prep():

    connection = get_connection()
    cursor = get_dict_cursor(connection)

    if request.method == "POST":
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
                request.form["sample_id"],
                session["user_id"],
                request.form["remark"]
            )
        )
        connection.commit()
        cursor.close()
        connection.close()
        return redirect(url_for("epdm_adhesion_prep"))
    
    
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
            LEFT JOIN epdm_adhesion_preparation
            ON epdm_adhesion_preparation.sample_id =
            samples.sample_id
            WHERE
                product_test_requirements.test_type_id = 7
            AND epdm_adhesion_preparation.sample_id IS NULL
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
            """
    )   

    samples = cursor.fetchall()
    cursor.execute(
        """
        SELECT
            samples.batch_nr,
            products.product_name,
            epdm_adhesion_preparation.prepared_date
        FROM epdm_adhesion_preparation
        JOIN samples
        ON samples.sample_id =
           epdm_adhesion_preparation.sample_id
        JOIN products
        ON products.product_id =
           samples.product_id
        LEFT JOIN epdm_adhesion
        ON epdm_adhesion.sample_id =
           samples.sample_id
        WHERE epdm_adhesion.sample_id IS NULL
        ORDER BY prepared_date DESC
        """
    )

    prepared = cursor.fetchall()
    cursor.close()
    connection.close()

    return render_template(
        "tests/epdm_adhesion/epdm_adhesion_prep.html",
        samples=samples,
        prepared=prepared,
        today=date.today()
    )

@app.route("/test/epdm_adhesion/test", methods=["GET","POST"])
@login_required
def epdm_adhesion_test():

    connection = get_connection()
    cursor = get_dict_cursor(connection)

    # Save new adhesion result

    if request.method == "POST":
 
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
            (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
            """,
            (
                request.form["sample_id"],
                session["user_id"],   
                request.form["remark"],
                request.form["europees"],
                request.form["trc"],
                request.form["carlisle"],
                request.form["rubber"],
                request.form["copper"],
                request.form["wood"],
                request.form["aluminium"],
                request.form["aluminium_anod"],
                request.form["lead"],
                request.form["rvs"],
                request.form["concrete"],
                request.form["glass"],
                request.form["pvc"],
                request.form["pmma"],
                request.form["pc"]
            )
        )
        connection.commit()
        cursor.close()
        connection.close()
        return redirect(url_for("epdm_adhesion_test"))

    # Products requiring adhesion testing
    cursor.execute(
        """
        SELECT
            products.product_id,
            products.product_name
        FROM products
        JOIN product_test_requirements
        ON product_test_requirements.product_id = products.product_id
        WHERE product_test_requirements.test_type_id = 7
        ORDER BY products.product_name
        """
    )
    products = cursor.fetchall()

    # Latest Adhesion results
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
        LIMIT 25
        """
    )
    results = cursor.fetchall()
    cursor.close()
    connection.close()
    return render_template(
        "tests/epdm_adhesion/epdm_adhesion_test.html",
        products=products,
        results=results
    )

@app.route("/get_epdm_adhesion_samples/<int:product_id>")
def get_epdm_adhesion_samples(product_id):

    connection = get_connection()
    cursor = get_dict_cursor(connection)
    cursor.execute(
        """
        SELECT
            samples.sample_id,
            samples.batch_nr

        FROM epdm_adhesion_preparation
        JOIN samples
        ON samples.sample_id = epdm_adhesion_preparation.sample_id
        LEFT JOIN epdm_adhesion
        ON epdm_adhesion.sample_id = samples.sample_id
        WHERE samples.product_id = %s
        AND epdm_adhesion.sample_id IS NULL
        AND epdm_adhesion_preparation.prepared_date::date
            <= CURRENT_DATE - INTERVAL '7 days'

        ORDER BY samples.sample_id
        """,
        (product_id,)
    )
    samples = cursor.fetchall()
    cursor.close()
    connection.close()
    return {
    "samples": [
        {
            "id": sample["sample_id"],
            "batch_nr": sample["batch_nr"]
        }
        for sample in samples
    ]
    }

@app.route("/test/curability")
@login_required
def curability():

    return render_template("tests/curability/curability.html")

@app.route("/test/curability/prep", methods=["GET", "POST"])
@login_required
def curability_prep():

    connection = get_connection()
    cursor = get_dict_cursor(connection)

    if request.method == "POST":
        sample_id = request.form["sample_id"]
        afterstorage_id = request.form.get("afterstorage_id") or None
        cursor.execute(
            """
            INSERT INTO curability_preparation
            (
                sample_id,
                operator_id,
                afterstorage_id,
                remark
            )
            VALUES
            (%s,%s,%s,%s)
            """,
            (
                sample_id,
                session["user_id"],
                afterstorage_id,
                request.form["remark"]
            )
        )

        connection.commit()
        cursor.close()
        connection.close()
        return redirect(url_for("curability_prep"))
    # Samples available for preparation
    cursor.execute(
        """
        SELECT
            samples.sample_id,
            NULL::INTEGER AS afterstorage_id,
            samples.batch_nr AS display_name,
            products.product_name
        FROM samples
        JOIN products
        ON products.product_id = samples.product_id
        JOIN product_test_requirements
        ON product_test_requirements.product_id =
           products.product_id
        LEFT JOIN curability_preparation
        ON curability_preparation.sample_id =
           samples.sample_id
        WHERE
            product_test_requirements.test_type_id = 2
        AND curability_preparation.sample_id IS NULL
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
        UNION ALL
        SELECT
            samples.sample_id,
            after_storage.afterstorage_id,
            samples.batch_nr || ' AS' AS display_name,
            products.product_name
        FROM after_storage
        JOIN samples
        ON samples.sample_id = after_storage.sample_id
        JOIN products
        ON products.product_id = samples.product_id
        LEFT JOIN curability_preparation
        ON curability_preparation.afterstorage_id =
        after_storage.afterstorage_id
        WHERE
            after_storage.removed_from_oven IS NOT NULL
            AND curability_preparation.afterstorage_id IS NULL
        ORDER BY sample_id
        """
    )
    samples = cursor.fetchall()

    samples = [
        {
            "sample_id": sample["sample_id"],
            "afterstorage_id": sample["afterstorage_id"],
            "display_name": sample["display_name"]
        }
        for sample in samples
    ]

    cursor.execute(
        """
        SELECT
            curability_preparation.curability_preparation_id,
            samples.sample_id,
            curability_preparation.afterstorage_id,
            CASE
                WHEN curability_preparation.afterstorage_id IS NOT NULL
                THEN samples.batch_nr || ' AS'
                ELSE samples.batch_nr
            END AS display_name,
            products.product_name,
            curability_preparation.prepared_date,
            curability_preparation.removed_24h_at,
            curability_preparation.removed_7d_at
        FROM curability_preparation
        JOIN samples
        ON samples.sample_id = curability_preparation.sample_id
        JOIN products
        ON products.product_id = samples.product_id
        LEFT JOIN curability
        ON (
            curability_preparation.afterstorage_id IS NULL
            AND curability.sample_id = samples.sample_id
        )
        OR (
            curability_preparation.afterstorage_id IS NOT NULL
            AND curability.afterstorage_id =
                curability_preparation.afterstorage_id
        )
        WHERE curability.cureability_id IS NULL
        ORDER BY curability_preparation.prepared_date DESC
        """
        )

    prepared = cursor.fetchall()
    cursor.close()
    connection.close()

    return render_template(
        "tests/curability/curability_prep.html",
        samples=samples,
        prepared=prepared,
        now=datetime.now()
    )

@app.route("/test/curability/remove_24h/<int:curability_preparation_id>", methods=["POST"])
def curability_remove_24h(curability_preparation_id):

    connection = get_connection()
    cursor = get_dict_cursor(connection)
    cursor.execute(
        """
        UPDATE curability_preparation
        SET removed_24h_at = CURRENT_TIMESTAMP
        WHERE curability_preparation_id = %s
        """,
        (curability_preparation_id,)
    )
    connection.commit()
    cursor.close()
    connection.close()
    return redirect(url_for("curability_prep"))

@app.route("/test/curability/remove_7d/<int:curability_preparation_id>", methods=["POST"])
def curability_remove_7d(curability_preparation_id):
    connection = get_connection()
    cursor = get_dict_cursor(connection)
    cursor.execute(
        """
        UPDATE curability_preparation
        SET removed_7d_at = CURRENT_TIMESTAMP
        WHERE curability_preparation_id = %s
        """,
        (curability_preparation_id,)
    )
    connection.commit()
    cursor.close()
    connection.close()
    return redirect(url_for("curability_prep"))

@app.route("/test/curability/test", methods=["GET","POST"])
@login_required
def curability_test():

    connection = get_connection()
    cursor = get_dict_cursor(connection)

    if request.method == "POST":
        sample_ids = request.form.getlist("sample_id[]")
        afterstorage_ids = request.form.getlist("afterstorage_id[]")
        day_1 = request.form.getlist("day_1[]")
        temp_day1 = request.form.getlist("temp_day1[]")
        rh_day1 = request.form.getlist("rh_day1[]")
        day_7 = request.form.getlist("day_7[]")
        temp_day7 = request.form.getlist("temp_day7[]")
        rh_day7 = request.form.getlist("rh_day7[]")
        remarks = request.form.getlist("remark[]")
        operator_id = session["user_id"]

        for i in range(len(sample_ids)):
            if sample_ids[i] == "":
                continue

            cursor.execute(
                """
                INSERT INTO curability
                (
                    sample_id,
                    afterstorage_id,
                    operator_id,
                    remark,
                    day_1,
                    temp_day1,
                    rh_day1,
                    day_7,
                    temp_day7,
                    rh_day7
                )
                VALUES
                (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                """,
                (
                    sample_ids[i],
                    afterstorage_ids[i],
                    operator_id,
                    remarks[i],
                    day_1[i],
                    temp_day1[i],
                    rh_day1[i],
                    day_7[i],
                    temp_day7[i],
                    rh_day7[i]
                )
            )
        connection.commit()
        return redirect(url_for("curability_test"))

    cursor.execute(
        """
        SELECT
            samples.sample_id,
            curability_preparation.afterstorage_id,
            CASE
                WHEN curability_preparation.afterstorage_id IS NOT NULL
                THEN samples.batch_nr || ' AS'
                ELSE samples.batch_nr
            END AS display_name,
            products.product_name
        FROM curability_preparation
        JOIN samples
        ON samples.sample_id = curability_preparation.sample_id
        JOIN products
        ON products.product_id = samples.product_id
        LEFT JOIN curability
        ON (
            curability_preparation.afterstorage_id IS NULL
            AND curability.sample_id = samples.sample_id
        )
        OR (
            curability_preparation.afterstorage_id IS NOT NULL
            AND curability.afterstorage_id =
                curability_preparation.afterstorage_id
        )
        WHERE curability.cureability_id IS NULL
        AND curability_preparation.removed_24h_at IS NOT NULL
        AND curability_preparation.removed_7d_at IS NOT NULL
        ORDER BY samples.sample_id
        """
    )

    samples = cursor.fetchall()


    cursor.execute(
        """
        SELECT
            products.product_id,
            products.product_name
        FROM products
        JOIN product_test_requirements
        ON product_test_requirements.product_id = products.product_id
        WHERE product_test_requirements.test_type_id = 2
        ORDER BY products.product_name
        """
    )
    products = cursor.fetchall()

  
    cursor.execute(
        """
        SELECT
            samples.batch_nr AS display_name,
            curability.day_1,
            curability.temp_day1,
            curability.rh_day1,
            curability.day_7,
            curability.temp_day7,
            curability.rh_day7
        FROM curability
        JOIN samples
        ON samples.sample_id = curability.sample_id
        ORDER BY curability.sample_id DESC
        LIMIT 25
        """
    )
    results = cursor.fetchall()
    cursor.close()
    connection.close()
    return render_template(
        "tests/curability/curability_test.html",
        samples=samples,
        results=results
    )

@app.route("/get_curability_samples/<int:product_id>")
def get_curability_samples(product_id):

    connection = get_connection()
    cursor = get_dict_cursor(connection)
    cursor.execute(
        """
        SELECT
            samples.sample_id,
            NULL::INTEGER AS afterstorage_id,
            samples.batch_nr AS display_name
        FROM curability_preparation
        JOIN samples
        ON samples.sample_id = curability_preparation.sample_id
        LEFT JOIN curability
        ON curability.sample_id = samples.sample_id
        WHERE samples.product_id = %s
        AND curability.sample_id IS NULL
        AND curability_preparation.removed_24h_at IS NOT NULL
        AND curability_preparation.removed_7d_at IS NOT NULL
        UNION ALL
        SELECT
            samples.sample_id,
            after_storage.afterstorage_id,
            samples.batch_nr || ' AS' AS display_name
        FROM after_storage
        JOIN samples
        ON samples.sample_id = after_storage.sample_id
        JOIN curability_preparation
        ON curability_preparation.afterstorage_id =
        after_storage.afterstorage_id
        LEFT JOIN curability
        ON curability.afterstorage_id =
        after_storage.afterstorage_id
        WHERE
            samples.product_id = %s
            AND curability_preparation.removed_24h_at IS NOT NULL
            AND curability_preparation.removed_7d_at IS NOT NULL
            AND curability.afterstorage_id IS NULL
        ORDER BY sample_id
        """,
        (product_id,)
    )
    samples = cursor.fetchall()
    cursor.close()
    connection.close()
    return {
        "samples": [
            {
                "sample_id": sample["sample_id"],
                "afterstorage_id": sample["afterstorage_id"],
                "display_name": sample["display_name"]
            }
            for sample in samples
        ]
    }

@app.route("/test/tensile")
@login_required
def tensile():

    return render_template("tests/tensile/tensile.html")

@app.route("/test/tensile/prep", methods=["GET","POST"])
@login_required
def tensile_prep():

    connection = get_connection()
    cursor = get_dict_cursor(connection)

    if request.method == "POST":
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
                request.form["sample_id"],
                session["user_id"],
                request.form["remark"]
            )
        )
        connection.commit()
        cursor.close()
        connection.close()
        return redirect(url_for("tensile_prep"))
    
    
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
            ORDER BY samples.batch_sequence
            """
    )   

    samples = cursor.fetchall()
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

    prepared = cursor.fetchall()
    cursor.close()
    connection.close()

    return render_template(
        "tests/tensile/tensile_prep.html",
        samples=samples,
        prepared=prepared,
        today=date.today()
    )

@app.route("/test/tensile/measure", methods=["GET", "POST"])
@login_required
def tensile_measure():

    connection = get_connection()
    cursor = get_dict_cursor(connection)

    if request.method == "POST":

        sample_id = request.form["sample_id"]

        specimen_numbers = request.form.getlist("specimen_no[]")

        width1 = request.form.getlist("width_1[]")
        width2 = request.form.getlist("width_2[]")
        width3 = request.form.getlist("width_3[]")

        thickness1 = request.form.getlist("thickness_1[]")
        thickness2 = request.form.getlist("thickness_2[]")
        thickness3 = request.form.getlist("thickness_3[]")

        for i in range(4):

            w1 = float(width1[i])
            w2 = float(width2[i])
            w3 = float(width3[i])

            t1 = float(thickness1[i])
            t2 = float(thickness2[i])
            t3 = float(thickness3[i])

            width_avg = round((w1 + w2 + w3) / 3, 3)
            thickness_avg = round((t1 + t2 + t3) / 3, 3)

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
                    sample_id,
                    specimen_numbers[i],

                    w1,
                    w2,
                    w3,
                    width_avg,

                    t1,
                    t2,
                    t3,
                    thickness_avg
                )
            )

        connection.commit()
        cursor.close()
        connection.close()
        return redirect(url_for("tensile_measure"))

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
        ORDER BY samples.sample_id
        """
    )

    samples = cursor.fetchall()
    cursor.close()
    connection.close()
    return render_template(
        "tests/tensile/tensile_measure.html",
        samples=samples
    )

@app.route("/test/tensile/test", methods=["GET", "POST"])
@login_required
def tensile_test():

    connection = get_connection()
    cursor = get_dict_cursor(connection)

    if request.method == "POST":

        specimen_ids = request.form.getlist("specimen_id[]")

        t_50 = request.form.getlist("t_50[]")
        t_100 = request.form.getlist("t_100[]")
        t_max = request.form.getlist("t_max[]")
        e_max = request.form.getlist("e_max[]")
        remark = request.form.getlist("remark[]")

        if len(remark) < len(specimen_ids):
            remark = [""] * len(specimen_ids)

        for i in range(len(specimen_ids)):

            cursor.execute(
                """
                UPDATE tensile_specimen
                SET
                    t_max = %s,
                    e_max = %s,
                    t_50 = %s,
                    t_100 = %s,
                    remark = %s
                WHERE specimen_id = %s
                """,
                (
                    t_max[i],
                    e_max[i],
                    t_50[i],
                    t_100[i],
                    remark[i],
                    specimen_ids[i]
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
                (%s, %s, %s)
                """,
                (
                    request.form["sample_id"],
                    session["user_id"],
                    ""  
                )
            )
        connection.commit()
        cursor.close()
        connection.close()
        return redirect(url_for("tensile_test"))

    # batches ready for testing
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
        ORDER BY samples.sample_id
        """
    )
    batches = cursor.fetchall()

    # latest results
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
        LIMIT 25
        """
    )

    results = cursor.fetchall()
    cursor.close()
    connection.close()

    return render_template(
        "tests/tensile/tensile_test.html",
        batches=batches,
        results=results
    )

@app.route("/get_tensile_specimens/<int:sample_id>")
def get_tensile_specimens(sample_id):

    connection = get_connection()
    cursor = get_dict_cursor(connection)
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


    specimens = cursor.fetchall()
    cursor.close()
    connection.close()

    return {
        "specimens": specimens
    }

@app.route("/products", methods=["GET", "POST"])
@login_required
def products():

    connection = get_connection()
    cursor = get_dict_cursor(connection)


    if request.method == "POST":
        product_code = request.form["product_code"]
        product_name = request.form["product_name"]
        # Create product
        cursor.execute(
            """
            INSERT INTO products
            (
                product_code,
                product_name
            )

            VALUES
            (%s,%s)

            RETURNING product_id
            """,
            (
                product_code,
                product_name
            )
        )
        product_id = cursor.fetchone()["product_id"]
        # Get selected tests
        selected_tests = request.form.getlist("required_tests")

        # Save test requirements
        for test_id in selected_tests:
            frequency = request.form.get(
                f"frequency_{test_id}",
                1
            )
            cursor.execute(
                """
                INSERT INTO product_test_requirements
                (
                    product_id,
                    test_type_id,
                    frequency
                )
                VALUES
                (%s,%s,%s)
                """,
                (
                    product_id,
                    test_id,
                    frequency
                )
            )
        connection.commit()
        cursor.close()
        connection.close()
        return redirect(url_for("products"))
    # Load products
    cursor.execute(
        """
        SELECT
            product_id,
            product_code,
            product_name
        FROM products
        ORDER BY product_name
        """
    )
    products = cursor.fetchall()
    # Load available tests
    cursor.execute(
        """
        SELECT
            test_type_id,
            test_name
        FROM test_types
        ORDER BY test_name
        """
    )

    tests = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template(
        "products.html",
        products=products,
        tests=tests
    )

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
    prod_date = request.args.get("prod_date")
    if prod_date == "":
        prod_date = None

    if not product_id:

        cursor.close()
        connection.close()

        return render_template(
            "overview.html",
            products=products,
            selected_product=None,
            columns=[],
            results=[],
            batch_nr="",
            prod_date=""
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
    if 1 in required_tests:
        columns.extend([
            ("Yield Stress", "yield_stress"),
            ("Vis @10", "vis_at_10")
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

    if 2 in required_tests:
        columns.extend([
            ("Day 1", "day_1"),
            ("Day 7", "day_7")
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
            COALESCE(rheology.yield_stress, rheology_as.yield_stress) AS yield_stress,
            COALESCE(rheology.vis_at_10, rheology_as.vis_at_10) AS vis_at_10,
            ROUND(initial_tack.initial_tack, 2) AS initial_tack,
            COALESCE(skinformation.tack_free_time, skinformation_as.tack_free_time) AS tack_free_time,
            COALESCE(skinformation.skinformation_time, skinformation_as.skinformation_time) AS skinformation_time,
            COALESCE(curability.day_1, curability_as.day_1) AS day_1,
            COALESCE(curability.day_7, curability_as.day_7) AS day_7,
            shore_a.shore_a_avg,
            ROUND(density.density_product, 2) AS density_product,
            ROUND(AVG(tensile_specimen.t_max),2) AS t_max,
            ROUND(AVG(tensile_specimen.e_max),2) AS e_max,
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
        LEFT JOIN rheology
            ON rheology.sample_id = samples.sample_id
        LEFT JOIN rheology AS rheology_as
            ON rheology_as.afterstorage_id = after_storage.afterstorage_id
        LEFT JOIN initial_tack
            ON initial_tack.sample_id = samples.sample_id
        LEFT JOIN skinformation
            ON skinformation.sample_id = samples.sample_id
        LEFT JOIN skinformation AS skinformation_as
            ON skinformation_as.afterstorage_id = after_storage.afterstorage_id
        LEFT JOIN curability
          ON curability.sample_id = samples.sample_id
        LEFT JOIN curability AS curability_as
          ON curability_as.afterstorage_id = after_storage.afterstorage_id
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

    if prod_date is not None:
        query += "\n            AND samples.prod_date = %s"
        query_args.append(prod_date)

    query += """

        GROUP BY
            samples.sample_id,
            samples.batch_nr,
            samples.prod_date,
            rheology.yield_stress,
            rheology.vis_at_10,
            rheology_as.yield_stress,
            rheology_as.vis_at_10,
            initial_tack.initial_tack,
            skinformation.tack_free_time,
            skinformation.skinformation_time,
            skinformation_as.tack_free_time,
            skinformation_as.skinformation_time,
            curability.day_1,
            curability.day_7,
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
    for title, field in columns:
        values = [
            row[field] for row in results
            if row[field] is not None and isinstance(row[field], Real)
        ]
        averages[field] = round(sum(values) / len(values), 2) if values else None

    cursor.close()
    connection.close()

    return render_template(
        "overview.html",
        products=products,
        selected_product=product_id,
        columns=columns,
        results=results,
        batch_nr=batch_nr,
        prod_date=prod_date or "",
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
                products.product_name
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
                            "Eu-EPDM": epdm_adhesion["europees"],
                            "TRC-EPDM": epdm_adhesion["trc"],
                            "CL-EPDM": epdm_adhesion["carlisle"],
                            "Rubber": epdm_adhesion["rubber"],
                            "Copper": epdm_adhesion["copper"],
                            "Wood": epdm_adhesion["wood"],
                            "Aluminium": epdm_adhesion["aluminium"],
                            "Aluminium Anod.": epdm_adhesion["aliminium_anod"],
                            "Lead": epdm_adhesion["lead"],
                            "RVS": epdm_adhesion["rvs"],
                            "Concrete": epdm_adhesion["concrete"],
                            "Glass": epdm_adhesion["glass"],
                            "PVC": epdm_adhesion["pvc"],
                            "PMMA": epdm_adhesion["pmma"],
                            "PC": epdm_adhesion["pc"]
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
    app.run(debug=False)