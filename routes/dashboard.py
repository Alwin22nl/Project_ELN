from flask import (
    Blueprint,
    request,
    session,
    redirect,
    render_template,
    url_for
)

from helper import login_required

from repositories.dashboard_repository import DashboardRepository
from services.dashboard_service import DashboardService

dashboard_bp = Blueprint(
    "dashboard",
    __name__
)

repository = DashboardRepository()
service = DashboardService(repository)

@dashboard_bp.route("/")
@login_required
def dashboard():
    context = service.get_dashboard_context()

    return render_template(
        "home.html",
        **context
    )

@dashboard_bp.route("/afterstorage/place", methods=["POST"])
@login_required
def place_afterstorage():
    service.place_afterstorage(
        sample_id=request.form["sample_id"],
        oven_location=request.form["oven_location"]
    )

    return redirect(
        url_for(".dashboard")
    )

@dashboard_bp.route("/afterstorage/remove", methods=["POST"])
@login_required
def remove_afterstorage():
    service.remove_afterstorage(
        afterstorage_id=request.form["afterstorage_id"]
    )

    return redirect(
        url_for(".dashboard")
    )