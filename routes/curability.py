from flask import(
    Blueprint,
    redirect,
    render_template,
    request,
    url_for,
    session
)

from datetime import datetime
from helper import login_required

from repositories.curability_repository import CurabilityRepository
from services.curability_service import CurabilityService

curability_bp = Blueprint(
    "curability",
    __name__,
    url_prefix="/test"
)

repository = CurabilityRepository()
service = CurabilityService(repository)

@curability_bp.route("/curability")
@login_required
def curability():

    return render_template("tests/curability/curability.html")

@curability_bp.route("/curability/curability_prep", methods=["GET", "POST"])
@login_required
def curability_prep():
    if request.method == "POST":
        service.submit_prep_result(
            request.form,
            operator_id=session["user_id"]
        )
        return redirect(
            url_for("curability.curability_prep")
        )

    products, results = service.get_prep_overview()

    return render_template(
        "tests/curability/curability_prep.html",
        products=products,
        results=results,
        now=datetime.now()
    )

@curability_bp.route("/curability/remove_24h/<int:curability_preparation_id>", methods=["POST"])
@login_required
def curability_remove_24h(curability_preparation_id):
    service.curability_remove_24h(
        curability_preparation_id
    )
    return redirect(
        url_for("curability.curability_prep")
    )


@curability_bp.route("/curability/remove_7d/<int:curability_preparation_id>", methods=["POST"])
@login_required
def curability_remove_7d(curability_preparation_id):
    service.curability_remove_7d(curability_preparation_id)
    return redirect(
        url_for("curability.curability_prep")
    )


@curability_bp.route("/curability/curability_test", methods=["GET", "POST"])
@login_required
def curability_test():
    if request.method == "POST":
        service.submit_test_result(
            request.form,
            operator_id=session["user_id"]
        )
        return redirect(
            url_for("curability.curability_test")
        )

    products, results = service.get_test_overview()

    return render_template(
        "tests/curability/curability_test.html",
        products=products,
        results=results
    )

@curability_bp.route("/get_curability_prep_samples/<int:product_id>")
@login_required
def get_curability_prep_samples(product_id):
    samples = service.get_samples_for_prep(product_id)

    return {
        "samples": samples
    }

@curability_bp.route("/get_curability_test_samples/<int:product_id>")
@login_required
def get_curability_test_samples(product_id):
    samples = service.get_samples_for_test(product_id)

    return {
        "samples": samples
    }