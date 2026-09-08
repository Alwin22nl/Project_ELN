from models.shore_a import ShoreAPrepResult, ShoreATestResult

class ShoreAService:
    def __init__(self, repository):
        self.repository = repository

    def submit_test_result(self, form, operator_id):
        result = ShoreATestResult(
            sample_id=form["sample_id"],
            operator_id=operator_id,
            remark=form["remark"],
            shore_a_1=float(form["shore_a_1"]),
            shore_a_2=float(form["shore_a_2"]),
            shore_a_3=float(form["shore_a_3"]),
            temperature=form["temperature"],
            humidity=form["humidity"],
        )
        shore_a_avg = result.calculate_avg_shore_a()
        self.repository.add_test_result(result, shore_a_avg)

    def submit_prep_result(self, form, operator_id):
        result = ShoreAPrepResult(
            sample_id=form["sample_id"],
            operator_id=operator_id,
            remark=form["remark"],
        )
        self.repository.add_prep_result(result)

    def get_test_overview(self):
        products = self.repository.get_required_products()
        results = self.repository.get_latest_results()

        return products, results

    def get_prep_overview(self):
        products = self.repository.get_required_products()
        results = self.repository.get_prep_list()

        return products, results
    
    def get_samples_for_prep(self, product_id):
        samples = self.repository.get_samples_for_prep(product_id)

        return [
            {
                "sample_id": sample["sample_id"],
                "display_name": sample["display_name"]
            }
            for sample in samples
        ]

    def get_samples_for_test(self, product_id):
        samples = self.repository.get_samples_for_test(product_id)

        return [
            {
                "sample_id": sample["sample_id"],
                "display_name": sample["display_name"]
            }
            for sample in samples
        ]  