from models.curability import CurabilityPrep, CurabilityTest

class CurabilityService:
    def __init__(self, repository):
        self.repository = repository

    def submit_prep_result(self, form, operator_id):
        result = CurabilityPrep(
            sample_id=form["sample_id"],
            operator_id=operator_id,
            remark=form["remark"],
        )
        self.repository.add_curability_prep(result)

    def curability_remove_24h(self, curability_preparation_id, operator_id):
        self.repository.curability_remove_24h(
            curability_preparation_id,
            operator_id
        )

    def curability_remove_7d(self, curability_preparation_id, operator_id):
        self.repository.curability_remove_7d(
            curability_preparation_id,
            operator_id
        )

    def submit_test_result(self, form, operator_id):
        sample_ids = form.getlist("sample_id[]")
        afterstorage_ids = form.getlist("afterstorage_id[]")
        remarks = form.getlist("remark[]")
        day_1s = form.getlist("day_1[]")
        temp_day1s = form.getlist("temp_day1[]")
        rh_day1s = form.getlist("rh_day1[]")
        day_7s = form.getlist("day_7[]")
        temp_day7s = form.getlist("temp_day7[]")
        rh_day7s = form.getlist("rh_day7[]")

        results = []

        for i in range(len(sample_ids)):
            if sample_ids[i] == "":
                continue

            afterstorage_id = None

            if i < len(afterstorage_ids):
                value = afterstorage_ids[i]

                if value != "":
                    afterstorage_id = value

            result = CurabilityTest(
                sample_id=sample_ids[i],
                operator_id=operator_id,
                afterstorage_id=afterstorage_id,
                remark=remarks[i],
                day_1=float(day_1s[i]),
                temp_day1=float(temp_day1s[i]),
                rh_day1=float(rh_day1s[i]),
                day_7=float(day_7s[i]),
                temp_day7=float(temp_day7s[i]),
                rh_day7=float(rh_day7s[i])
            )

            results.append(result)

        self.repository.add_results(results)

    def get_prep_overview(self):
        products = self.repository.get_required_products()
        results = self.repository.get_prep_list()

        return products, results

    def get_test_overview(self):
        products = self.repository.get_required_products()
        results = self.repository.get_latest_results()

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