from functools import wraps
from psycopg2.errors import UniqueViolation
from helper import login_required

from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    session,
    abort
)

from repositories.limits_repository import LimitsRepository
from services.limit_service import LimitsService

limits_bp = Blueprint("limits", __name__)

limits_repository = LimitsRepository()
limits_service = LimitsService(limits_repository)

def admin_required(view):
    @wraps(view)
    @login_required
    def wrapped(*args, **kwargs):
        if str(session.get("role", "")).lower() != "admin":
            abort(403)

        return view(*args, **kwargs)

    return wrapped

@limits_bp.route("/limits", methods=["GET"])
@admin_required
def manage_limits():
    products = limits_repository.get_products_for_limits()
    selected_product_id = request.args.get(
        "product_id",
        type=int
    )

    if selected_product_id is None and products:
        selected_product_id = products[0]["product_id"]

    product_ids = {
        product["product_id"]
        for product in products
    }

    if (
        selected_product_id is not None 
        and selected_product_id not in product_ids
    ):
        abort(404)

    product_limits = []

    if selected_product_id is not None:
        product_limits = limits_service.get_product_limits(selected_product_id)

    return render_template(
        "limits.html",
        products=products,
        selected_product_id=selected_product_id,
        product_limits=product_limits,
        limit_config=limits_service.get_available_tests()
    )

@limits_bp.route("/limits/create", methods=["POST"])
@admin_required
def create_limit():
    product_id = request.form.get(
        "product_id",
        type=int
    )

    if product_id is None:
        flash("Selecteer een geldig product.", "error")
        return redirect(url_for("limits.manage_limits"))

    try:
        limits_service.create_limit(
            product_id=product_id,
            test_key=request.form.get("test_key"),
            field_name=request.form.get("field_name"),
            test_stage=request.form.get("test_stage"),
            min_value=request.form.get("min_value"),
            max_value=request.form.get("max_value"),
            created_by=session["user_id"]
        )

        flash("Limiet succesvol toegevoegd.", "success")

    except UniqueViolation:
        flash(
            "Er bestaat al een actieve limiet "
            "voor deze test en dit resultaat.",
            "error"
        )

    except ValueError as error:
        flash(str(error), "error")

    return redirect(url_for(
        "limits.manage_limits",
        product_id=product_id
    ))

@limits_bp.route("/limits/<int:limit_id>/replace", methods=["POST"])
@admin_required
def replace_limit(limit_id):
    existing_limit = limits_repository.get_limit_by_id(limit_id)

    if existing_limit is None:
        abort(404)

    product_id = existing_limit["product_id"]

    try:
        limits_service.replace_limit(
            limit_id=limit_id,
            min_value=request.form.get("min_value"),
            max_value=request.form.get("max_value"),
            created_by=session["user_id"]
        )

        flash("Limiet succesvol aangepast.", "success")

    except ValueError as error:
        flash(str(error), "error")

    except UniqueViolation:
        flash(
            "Er bestaat al een actieve limiet "
            "voor dit resultaat",
            "error"
        )

    return redirect(url_for(
        "limits.manage_limits",
        product_id=product_id
    ))

@limits_bp.route("/limits/<int:limit_id>/deactivate", methods=["POST"])
@admin_required
def deactivate_limit(limit_id):
    existing_limit = limits_repository.get_limit_by_id(limit_id)

    if existing_limit is None:
        abort(404)

    product_id = existing_limit["product_id"]
    success = limits_service.deactivate_limit(limit_id)

    if success:
        flash("Limiet gedeactiveerd.", "success")

    else: 
        flash("Limiet was al inactief", "error")

    return redirect(url_for(
        "limits.manage_limits",
        product_id=product_id
    ))