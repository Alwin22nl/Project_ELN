from flask import (
    Blueprint,
    redirect,
    render_template,
    request,
    url_for,
    session
)
from helper import login_required

from repositories.rheology_repository import RheologyRepository
from services.rheology_service import RheologyService

rheology_bp = Blueprint(
    "rheology",
    __name__,
    url_prefix="/test"
)

repository = RheologyRepository()
service = RheologyService(repository)

@rheology_bp.route("/rheology", methods=["GET", "POST"])
@login_required
def rheology():

    if request.method == "POST":
        service.submit_result(
            request.form,
            operator_id=session["user_id"]
        )

        return redirect(
            url_for("rheology.rheology")
        )
    products, results = service.get_overview()

    return render_template(
        "tests/rheology.html",
        products=products,
        results=results
    )

