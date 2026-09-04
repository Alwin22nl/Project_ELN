from models.skinformation import skinformationresult

class SkinformationService:
    def __init__(self, repository):
        self.repository = repository

    def submit_result(self, form, operator_id):
        result = skinformationresult(
            sample_id=form["sample_id"],
            afterstorage_id=form.get("afterstorage_id") or None,
            operator_id=operator_id,
            remark=form["remark"],
            skinformation_time=form["skinformation_time"],
            temp_skinformation_time=form["temp_skinformation_time"],
            rh_skinformation_time=form["rh_skinformation_time"],
            tack_free_time=form["tack_free_time"],   
            temp_tack_free_time=form["temp_tack_free_time"],
            rh_tack_free_time=form["rh_tack_free_time"]
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