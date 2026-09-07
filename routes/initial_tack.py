from flask import (
    Blueprint,
    redirect,
    render_template,
    request,
    url_for,
    session
)
from helper import login_required

from repositories.initial_tack_repository import InitialTackRepository
from services.initial_tack_service import InitialTackService

initial_tack_bp = Blueprint(
    "initial_tack",
    __name__,
    url_prefix="/test"
)

repository = InitialTackRepository()
service = InitialTackService(repository)

@initial_tack_bp.route("/initial_tack", methods=["GET", "POST"])
@login_required
def initial_tack():
    if request.method == "POST":
        service.submit_result(
            request.form,
            operator_id=session["user_id"]
        )

        return redirect(
            url_for("initial_tack.initial_tack")
        )
    products, results = service.get_overview()

    return render_template(
        "tests/initial_tack.html",
        products=products,
        results=results
    )

@initial_tack_bp.route("/get_initial_tack_samples/<int:product_id>")
@login_required
def get_initial_tack_samples(product_id):

    samples = service.get_available_samples(product_id)

    return {
        "samples": samples
    }