from flask import(
    Blueprint,
    redirect,
    render_template,
    request,
    url_for,
    session,
    flash,
    jsonify
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
                request.form,
                requested_by=session["user_id"]
            )

            flash(
                "Wijzigingsaanvraag is ingediend!",
                "success"
            )

            return redirect(
                url_for(".create_request")
            )

        except ValueError as e:
            flash(str(e), "error")

    products = service.get_products()

    return render_template(
        "change_request/create.html",
        products=products
    )

@change_request_bp.route("/change_request/batches")
@login_required
def get_batches():
    product_id = request.args.get("product_id", type=int)
    batches = service.get_batches(product_id)

    return jsonify(batches)

@change_request_bp.route("/change_request/tests")
@login_required
def get_tests():
    sample_id = request.args.get("sample_id", type=int)
    tests = service.get_available_tests(sample_id)

    return jsonify(tests)

@change_request_bp.route("/change_request/fields")
@login_required
def get_fields():
    test_key = request.args.get("test_key")
    record_id = request.args.get("record_id", type=int) 

    fields = service.get_changeable_fields(test_key, record_id)
    return jsonify(fields)

@change_request_bp.route("/change_request/my_requests")
@login_required
def my_requests():

    change_requests = service.get_requests_by_user(
        session["user_id"]
    )

    return render_template(
        "change_request/my_requests.html",
        change_requests=change_requests
    )