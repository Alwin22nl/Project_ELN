from flask import (
    Blueprint,
    render_template,
    request
)

from helper import login_required

from repositories.batch_search_repository import BatchSearchRepository
from services.batch_search_service import BatchSearchService

batch_search_bp = Blueprint(
    "batch_search",
    __name__
)

repository = BatchSearchRepository()
service = BatchSearchService(repository)

@batch_search_bp.route("/batch_search",methods=["GET", "POST"])
@login_required
def batch_search():

    batch = None
    batches = []
    results = []
    remarks = []

    if request.method == "POST":
        batch_nr = request.form["batch_nr"].strip()
        (
            batch,
            batches,
            results,
            remarks
        ) = service.search_batch(batch_nr)

    return render_template(
        "batch_search.html",
        batch=batch,
        batches=batches,
        results=results,
        remarks=remarks
    )