from models.products import Product

class ProductService:
    def __init__(self, repository):
        self.repository = repository

    def create_product(self, form):
        product = Product(
            product_code=form["product_code"],
            product_name=form["product_name"]
        )

        selected_tests = form.getlist("required_tests")

        requirements = []

        for test_id in selected_tests:
            frequency = form.get(f"frequency_{test_id}", 1)
            requirements.append({
                "test_type_id": int(test_id),
                "frequency": int(frequency)
            })

        self.repository.create_product(product, requirements)

    def get_products_overview(self):
        products = self.repository.get_products()
        tests = self.repository.get_test_types()

        return products, tests

    