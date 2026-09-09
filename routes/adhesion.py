from flask import(
    Blueprint,
    redirect,
    render_template,
    request,
    url_for,
    session
)

from datetime import date
from helper import login_required

from repositories.adhesion_repository import AdhesionRepository
from services.adhesion_service import AdhesionService

adhesion_bp = Blueprint(
    "adhesion",
    __name__,
    url_prefix="/test"
)

repository = AdhesionRepository()
service = AdhesionService()

@adhesion_bp.route("/adhesion")
@login_required
def adhesion():

    return render_template("tests/adhesion/adhesion.html")

@adhesion_bp.route("/adhesion/adhesion_prep", methods=["GET", "POST"])
@login_required
def adhesion_prep():
    if request.method == "POST":
        service.submit_prep_result(
            request.form,
            operator_id=session["user_id"]
        )
        return redirect(
            url_for("adhesion.adhesion_prep")
        )
    products, results = service.get_prep_overview()

    return render_template(
        "tests/adhesion/adhesion_prep.html",
        products=products,
        results=results,
        today=date.today()
    )

@adhesion_bp.route("/adhesion/adhesion_test", methods=["GET", "POST"])
@login_required
def adhesion_test():
    if request.method == "POST":
        service.submit_test_result(
            request.form,
            operator_id=session["user_id"]
        )

        return redirect(
            url_for("adhesion.adhesion_test")
        )

    products, results = service.get_test_overview()

    return render_template(
        "tests/adhesion/adhesion_test.html",
        products=products,
        results=results
    )

@adhesion_bp.route("/get_adhesion_prep_samples/<int:product_id>")
@login_required
def get_adhesion_prep_sample(product_id):
    samples = service.get_samples_for_prep(product_id)

    return {
        "samples": samples
    }

@adhesion_bp.route("/get_adhesion_test_samples/<int:product_id>")
@login_required
def get_adhesion_test_samples(product_id):
    samples = service.get_samples_for_test(product_id)

    return {
        "samples": samples
    }