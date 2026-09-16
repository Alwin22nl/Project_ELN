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
            prod_date=date.fromisoformat(form["prod_date"]),
            product_id=int(form["product_id"]),
            afterstorage_required=(form.get("after_storage_required") == "true"),
            remark=form["remark"],
        )

        next_sequence = self.repository.get_next_sequence(sample.product_id)

        self.repository.add_sample(sample, next_sequence)

        return None

    def get_overview(self):
        products = self.repository.get_products()
        samples = self.repository.get_recent_samples()

        if not samples:
            return products, []

        sample_ids = [
            sample["sample_id"]
            for sample in samples
        ]

        product_ids = list([
            sample["product_id"]
            for sample in samples
        ])

        requirements = self.repository.get_required_tests(
            product_ids
        )

        completed_tests = {}

        completed_rows = self.repository.get_completed_tests(
            sample_ids
        )

        required_tests = {}

        for row in requirements:
            required_tests.setdefault(
                row["product_id"],
                set()
            ).add(
                row["test_type_id"]
            )

        sample_list = []
        current_date = date.today()

        for sample in samples:
            due_date = (
                sample["prod_date"]
                + timedelta(days=7)
            )

            required = required_tests.get(
                sample["sample_id"],
                set()
            )

            completed = completed_tests.get(
                sample["sample_id"],
                set()
            )

            all_tests_completed = required.issubset(
                completed
            )

            if all_tests_completed:
                status = "🟢 Completed"

            elif current_date < due_date:
                status = "🔴 Wait with Testing"

            else: 
                status = "🟠 Available for Testing / in progress"

            sample_list.append({
                "batch_nr": sample["batch_nr"],
                "product": sample["product"],
                "prod_date": sample["prod_date"],
                "due_date": due_date,
                "status": status,
            })

        return products, sample_list