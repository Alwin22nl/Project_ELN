from flask import(
    Blueprint,
    render_template,
    redirect,
    request,
    url_for,
    session,
    jsonify,
    flash
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

    if request.method == "POST":

        error = service.register_sample(request.form)
        if error:
            flash(error, "error")

        else:
            flash("Batch met succes aangemaakt!", "success")
            return redirect(url_for(".sample"))

    products, samples = service.get_overview()

    return render_template(
        "sample.html",
        products=products,
        samples=samples
    )

@sample_bp.route("/sample/append_remark", methods=["POST"])
@login_required
def sample_append_remark():
    sample_id = request.form.get("sample_id")
    remark = request.form.get("remark")

    user = (
        session.get("name")
        or session.get("username")
        or "unknown"
    )

    service.append_remark(
        sample_id=sample_id,
        remark=remark,
        user=user
    )

    return redirect(
        url_for(".sample")
    )

@sample_bp.route("/get_samples/<int:product_id>")
@login_required
def get_samples(product_id):
    samples = service.get_samples_by_product(product_id)

    return jsonify(samples)