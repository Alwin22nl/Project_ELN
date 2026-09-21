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