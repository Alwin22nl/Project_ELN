from flask import(
    Blueprint,
    redirect,
    render_template,
    url_for,
    request,
    session
)

from datetime import date
from helper import login_required

from repositories.tensile_repository import TensileRepository
from services.tensile_service import TensileService

tensile_bp = Blueprint(
    "tensile",
    __name__,
    url_prefix="/test"
)

repository = TensileRepository()
service = TensileService(repository)

@tensile_bp.route("/tensile")
@login_required
def tensile():

    return render_template("tests/tensile/tensile.html")

@tensile_bp.route("/tensile/tensile_prep", methods=["GET", "POST"])
@login_required
def tensile_prep():
    if request.method == "POST":
        service.submit_prep_result(
            request.form,
            operator_id=session["user_id"]
        )
        return redirect(
            url_for("tensile.tensile_prep")
        )
    products, results = service.get_prep_overview()

    return render_template(
        "tests/tensile/tensile_prep.html",
        products=products,
        results=results,
        today=date.today()
    )

@tensile_bp.route("/tensile/tensile_measure", methods=["GET", "POST"])
@login_required
def tensile_measure():
    if request.method == "POST":
        service.submit_measurements(
            request.form
        )
        return redirect (
            url_for("tensile.tensile_measure")
        )

    return render_template(
        "tests/tensile/tensile_measure.html"
    )

@tensile_bp.route("/tensile/tensile_test", methods=["GET", "POST"])
@login_required
def tensile_test():
    if request.method == "POST":
        service.submit_test_result(
            request.form,
            operator_id=session["user_id"]
        )
        return redirect(
            url_for("tensile.tensile_test")
        )
    products, results = service.get_test_overview()

    return render_template(
        "tests/tensile/tensile_test.html",
        products=products,
        results=results
    )

@tensile_bp.route("/get_tensile_prep_samples")
@login_required
def get_tensile_prep_sample():
    samples = service.get_samples_for_prep()

    return {
        "samples": samples
    }

@tensile_bp.route("/get_tensile_measure_samples")
@login_required
def get_tensile_measure_sample():
    samples = service.get_samples_for_measurement()

    return {
        "samples": samples
    }

@tensile_bp.route("/get_tensile_test_samples")
@login_required
def get_tensile_test_sample():
    samples = service.get_samples_for_test()

    return {
        "samples": samples
    }