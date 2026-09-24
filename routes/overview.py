from flask import (
    Blueprint,
    render_template,
    request,
    jsonify
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

@overview_bp.route("/overview/result_details")
@login_required
def result_details():

    sample_id = request.args.get(
        "sample_id",
        type=int
    )

    test_type = request.args.get(
        "test_type"
    )

    afterstorage = (
        request.args.get("afterstorage")
        == "true"
    )

    details = service.get_result_details(
        sample_id=sample_id,
        test_type=test_type,
        afterstorage=afterstorage
    )

    return jsonify(details)