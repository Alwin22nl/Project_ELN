from flask import(
    Blueprint,
    redirect,
    render_template,
    request,
    url_for,
    session
)

from helper import login_required

from repositories.shore_a_repository import ShoreARepository
from services.shore_a_service import ShoreAService

shore_a_bp = Blueprint(
    "shore_a",
    __name__,
    url_prefix="/test" 
)

repository = ShoreARepository()
service = ShoreAService(repository)

@shore_a_bp.route("/shore_a")
@login_required
def shore_a():

    return render_template("tests/shore_a/shore_a.html")

@shore_a_bp.route("/shore_a/shore_a_prep", methods=["GET", "POST"])
@login_required
def shore_a_prep():
    if request.method == "POST":
        service.submit_prep_result(
            request.form,
            operator_id=session["user_id"]
        )

        return redirect(
            url_for("shore_a.shore_a_prep")
        )
    
    products, results = service.get_prep_overview()

    return render_template(
        "tests/shore_a/shore_a_prep.html",
        products=products,
        results = results
    )

   

@shore_a_bp.route("/shore_a/shore_a_test", methods=["GET", "POST"])
@login_required
def shore_a_test():
    if request.method == "POST":
        service.submit_test_result(
            request.form,
            operator_id=session["user_id"]
        )

        return redirect(
            url_for("shore_a.shore_a_test")
        )
    
    products, results = service.get_test_overview()

    return render_template(
        "tests/shore_a/shore_a_prep.html",
        products=products,
        results = results
    )

  
@shore_a_bp.route("/get_shore_a_prep_samples/<int:product_id>")
@login_required
def get_shore_a_prep_samples(product_id):
    samples = service.get_samples_for_prep(product_id)

    return {
        "samples": samples
    }

@shore_a_bp.route("/get_shore_a_test_samples/<int:product_id>")
@login_required
def get_shore_a_test_samples(product_id):

    samples = service.get_samples_for_test(product_id)

    return {
        "samples": samples
    }
