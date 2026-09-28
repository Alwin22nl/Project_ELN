from flask import(
    Blueprint,
    redirect,
    render_template,
    request,
    url_for,
    session,
    flash
)

from datetime import date
from helper import login_required

from repositories.change_request_repository import ChangeRequestRepository
from services.change_request_service import ChangeRequestService

change_request_bp = Blueprint(
    "change_request",
    __name__
)

repository = ChangeRequestRepository()
service = ChangeRequestService(repository)

@change_request_bp.route("/change_request/create", methods=["GET", "POST"])
@login_required
def create_request():
    if request.method == "POST":
        try:
            service.create_request(
                requested_by=session["user_id"],
                table_name=request.form["table_name"],
                record_id=int(request.form["record_id"]),
                field_name=request.form["field_name"],
                old_value=request.form["old_value"],
                new_value=request.form["new_value"],
                reason=request.form["reason"]
            )

            flash("wijzigingsaanvraag is ingediend!", "success")

            return redirect(
                url_for(".create_request")
            )

        except ValueError as e:
            flash(str(e), "error")

    return render_template(
        "change_requests/create/html"
    )