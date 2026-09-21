from flask import (
    Blueprint,
    render_template,
    redirect,
    url_for,
    request
)

from helper import login_required

from repositories.products_repository import ProductsRepository
from services.products_service import ProductService

product_bp = Blueprint(
    "product",
    __name__
)

repository = ProductsRepository()
service = ProductService(repository)

@product_bp.route("/products", methods=["GET", "POST"])
@login_required
def products():
    if request.method == "POST":
        service.create_product(
            request.form
        )

        return redirect(
            url_for(".products")
        )

    products, tests = service.get_products_overview()

    return render_template(
        "products.html",
        products=products,
        tests=tests
    )