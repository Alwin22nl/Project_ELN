from flask import (
    Blueprint,
    render_template,
    request
)

from helper import login_required

from repositories.overview_repository import OverviewRepository
from services.overview_service import OverviewService

overview_bp = Blueprint(
    "overview",
    __name__
)

repository = OverviewRepository()
service = OverviewService(repository)

@overview_bp.route("/overview")
@login_required
def overview_page():
    context = service.get_overview(
        product_id=request.args.get(
            "product_id",
            type=int
        ),
        batch_nr=request.args.get(
            "batch_nr",
            ""
        ).strip(),
        prod_date_from=request.args.get(
            "prod_date_from",
            ""
        ).strip(),
        prod_date_to=request.args.get(
            "prod_date_to",
            ""
        ).strip()
    )

    return render_template(
        "overview.html",
        **context
    )   