from models.initial_tack import InitialTackResult

class InitialTackService:
    def __init__(self, repository):
        self.repository = repository

    def submit_result(self, form, operator_id):
        result = InitialTackResult(
            sample_id=form["sample_id"],
            operator_id=operator_id,
            remark=form["remark"],
            area=float(form["area"]),
            area_weight=float(form["area_weight"]),
            added_weight=float(form["added_weight"]),
            humidity=form["humidity"], 
        )
        initial_tack = result.calculate_initial_tack()
        self.repository.add_result(result, initial_tack)

    def get_overview(self):
        products = self.repository.get_required_products()
        results = self.repository.get_latets_results

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
