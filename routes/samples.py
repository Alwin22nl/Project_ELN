from flask import(
    Blueprint,
    render_template,
    redirect,
    request,
    url_for
)

from helper import login_required

from repositories.samples_repository import SampleRepository
from services.samples_service import SamplesService

sample_bp = Blueprint(
    "sample",
    __name__
)

repository = SampleRepository()
service = SamplesService(repository)

@sample_bp.route("/sample", methods=["GET", "POST"])
@login_required
def sample():

    error = None

    if request.method == "POST":
        error = service.register_sample(
            request.form
        )

        if error is None:
            return redirect(
                url_for(".sample")
            )

    products, samples = service.get_overview()

    return render_template(
        "sample.html",
        products=products,
        samples=samples,
        error=error
    )