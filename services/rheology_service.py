from models.rheology import RheologyResult

class RheologyService:
    def __init__(self, repository):
        self.repository = repository

    def submit_result(self, form, operator_id):
        result = RheologyResult(
            sample_id=form["sample_id"],
            afterstorage_id=form.get("afterstorage_id") or None,
            operator_id=operator_id,
            remark=form["remark"],
            yield_stress=form["yield_stress"],
            vis_at_1=form["vis_at_1"],
            vis_at_5=form["vis_at_5"],
            vis_at_10=form["vis_at_10"],   
            humidity=form["humidity"]
        )

        self.repository.add_result(result)
    def get_overview(self):
        products = self.repository.get_required_products()
        results = self.repository.get_latest_results()

        return products, results

    def get_available_samples(self, product_id):
        samples = self.repository.get_available_samples(product_id)

        return [
            {
                "sample_id": sample["sample_id"],
                "afterstorage_id": sample["afterstorage_id"],
                "display_name": sample["display_name"]
            }
            for sample in samples
        ]