from datetime import date, timedelta
from models.samples import Samples

class SamplesService:
    def __init__(self, repository):
        self.repository = repository

    def register_sample(self, form):
        batch_nr = form["batch_nr"]

        if self.repository.batch_exists(batch_nr):
            return f"Batch Nummer '{batch_nr}' bestaat al."

        sample = Samples(
            batch_nr=batch_nr,
            prod_date=fromisoformat(form["prod_date"]),
            product_id=int(form["product_id"]),
            afterstorage_required=(form.get("after_storage_required") == "true"),
            remark=form["remark"]
        )

        next_sequence = self.repository.get_next_sequence(sample.product_id)

        self.repository.add_sample(sample, next_sequence)

        return None
    