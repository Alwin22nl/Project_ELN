from models.rheology import rheologyResult

class RheologyService:
    def __init__(self, repository):
        self.repository = repository

    def submit_result(self, form, operator_id):
        result = rheologyResult(
            sample_id=form["sample_id"],
            afterstorage_id=form.get("afterstorage_id") or None,
            operator_id=operator_id,
            remark=form["remark"],
            yieldstress=form["yieldstress"],
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