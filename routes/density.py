from flask import(
    Blueprint,
    redirect,
    render_template,
    request,
    url_for
    session
)
from helper import login_required

from repositories.density_repository import DensityRepository
from services.density_service import DensityService

density_bp = Blueprint(
    "density",
    __name__,
    url_prefix="/test"
)

repository = DensityRepository()
service = DensityService(repository)

@density_bp.route("/density", methods=["GET", "POST"])
@login_required
def density()
    if request.method == "POST"
        service.submit_result(
            request.form,
            operator_id=session["user_id"]
        )

        return redirect(
            url_for("density.density")
        )
    products, results = service.get_overview()

    return render_template(
        "tests/density.html",
        products=products,
        results=results
    )

@density_bp.route("/get_density_samples/<int:product_id>")
@login_required
def get_density_samples(product_id)

    samples = service.get_available_samples(product_id)

    return {
        "samples": samples
    }

