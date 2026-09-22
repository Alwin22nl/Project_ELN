from models.density import DensityResult

class DensityService:
    def __init__(self, repository):
        self.repository = repository

    def submit_result(self, form, operator_id):
        result = DensityResult(
            sample_id=form["sample_id"],
            operator_id=operator_id,
            remark=form["remark"],
            vessel_empty=float(form["vessel_empty"]),
            vessel_full=float(form["vessel_full"]),
            vessel_volume=float(form["vessel_volume"]),
        )
        density_product = result.calculate_density()
        self.repository.add_result(result, density_product)

    def get_overview(self):
        products = self.repository.get_required_products()
        results = self.repository.get_latest_results()

        return products, results

    def get_available_samples(self, product_id):
        samples = self.repository.get_available_samples(product_id)

        return [
            {
                "sample_id": sample["sample_id"],
                "display_name": sample["display_name"]
            }
            for sample in samples
        ]