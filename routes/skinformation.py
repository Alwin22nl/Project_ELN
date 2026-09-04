from flask import (
    Blueprint,
    redirect,
    render_template,
    request,
    url_for,
    session
)
from helper import login_required

from repositories.skinformation_repository import SkinformationRepository
from services.skinformation_service import SkinformationService

skinformation_bp = Blueprint(
    "skinformation",
    __name__,
    url_prefix="/test"
)

repository = SkinformationRepository()
service = SkinformationService(repository)

@skinformation_bp.route("/skinformation", methods=["GET", "POST"])
@login_required
def skinformation():

    if request.method == "POST":
        service.submit_result(
            request.form,
            operator_id=session["user_id"]
        )

        return redirect(
            url_for("skinformation.skinformation")
        )
    samples = service.get_available_samples()

    return render_template(
        "tests/skinformation.html",
        samples=samples,
    )
