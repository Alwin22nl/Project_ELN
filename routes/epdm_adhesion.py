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

from repositories.epdm_adhesion_repository import EpdmAdhesionRepository
from services.epdm_adhesion_service import EpdmService

epdm_adhesion_bp = Blueprint(
    "epdm_adhesion",
    __name__,
    url_prefix="/test"
)

repository = EpdmAdhesionRepository()
service = EpdmService(repository)

@epdm_adhesion_bp.route("/epdm_adhesion")
@login_required
def epdm_adhesion():

    return render_template("tests/epdm_adhesion/epdm_adhesion.html")

@epdm_adhesion_bp.route("/epdm_adhesion/epd_andhesion_prep", methods=["GET", "POST"])
@login_required
def epdm_adhesion_prep():
    if request.method == "POST":
        service.submit_prep_result(
            request.form,
            operator_id=session["user_id"]
        )
        return redirect(
            url_for("epdm_adhesion.epdm_adhesion_prep")
        )
    products, results = service.get_prep_overview()

    return render_template(
        "tests/epdm_adhesion/epdm_adhesion_prep.html",
        products=products,
        results=results,
        todat=date.today()
    )

@epdm_adhesion_bp.route("/epdm_adhesion/epdm_adhesion_test", methods=["GET", "POST"])
@login_required
def epdm_adhesion_test():
    if request.method == "POST":
        service.submit_test_result(
            request.form,
            operator_id=session["user_id"]
        )

        return redirect(
            url_for("epdm_adhesion.epdm_adhesion_test")
        )
    
    products, results = service.get_test_overview()

    return render_template(
        "tests/epdm_adhesion/epdm_adhesion_test.html",
        products=products,
        results=results
    )

@epdm_adhesion_bp.route("/get_epdm_adhesion_prep_samples/<int:product_id>")
@login_required
def get_epdm_adhesion_prep_sample(product_id):
    samples = service.get_samples_for_prep(product_id)

    return {
        "samples": samples
    }

@epdm_adhesion_bp.route("/get_epdm_adhesion_test_samples/<int:product_id>")
@login_required
def get_epdm_adhesion_test_sample(product_id):
    samples = service.get_samples_for_test(product_id)

    return {
        "samples": samples
    }