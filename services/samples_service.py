from datetime import date, timedelta, datetime
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

            all_tests_completed = (
                bool(required)
                and required.issubset(completed)
            )

            if all_tests_completed:
                status = "🟢 Completed"

            elif current_date < due_date:
                status = "🔴 Wait with Testing"

            else: 
                status = "🟠 Available for Testing / in progress"

            sample_list.append({
                "batch_nr": sample["batch_nr"],
                "product": sample["product_name"],
                "prod_date": sample["prod_date"],
                "due_date": due_date,
                "status": status,
            })

        return products, sample_list

    def append_remark(self, sample_id, remark, user):
        if not sample_id or not remark:
            return False
        timestamp = datetime.now().strftime("%d-%m-%Y %H-%M")

        appended = (
            f"{remark} "
            f"({timestamp} by {user})"
        )

        self.repository.append_remark(sample_id, appended)

        return True

    def get_samples_by_product(self, product_id):
        rows = self.repository.get_samples_by_product(product_id)

        results = []

        for row in rows:
            display = row["batch_nr"] or ""

            if row.get("prod_date"):
                formatted_date = row["prod_date"].strftime("%d-%m-%y")

                if display:
                    display = f"{display} - {formatted_date}"
                else:
                    display = formatted_date

            results.append({
                "sample_id": row["sample_id"],
                "display": display,
                "remark": row.get("remakr")
            })

        return results