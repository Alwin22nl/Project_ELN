from models.skinformation import SkinformationResult

class SkinformationService:
    def __init__(self, repository):
        self.repository = repository

    def submit_result(self, form, operator_id):
            sample_ids = form.getlist("sample_id[]")
            afterstorage_ids = form.getlist("afterstorage_id[]")
            remarks = form.getlist("remark[]")
            skin_times = form.getlist("skinformation_time[]")
            skin_temps = form.getlist("temp_skinformation_time[]")
            skin_rhs = form.getlist("rh_skinformation_time[]")
            tack_times = form.getlist("tack_free_time[]")
            tack_temps = form.getlist("temp_tack_free_time[]")
            tack_rhs = form.getlist("rh_tack_free_time[]")

            results = []

            for i in range(len(sample_ids)):
                if sample_ids[i] == "":
                    continue

                afterstorage_id = None

                if i < len(afterstorage_ids):
                    value = afterstorage_ids[i]

                    if value != "":
                        afterstorage_id = value

                result = SkinformationResult(
                    sample_id=sample_ids[i],
                    operator_id=operator_id,
                    afterstorage_id=afterstorage_id,
                    remark=remarks[i],
                    skinformation_time=skin_times[i],
                    temp_skinformation_time=skin_temps[i],
                    rh_skinformation_time=skin_rhs[i],
                    tack_free_time=tack_times[i],
                    temp_tack_free_time=tack_temps[i],
                    rh_tack_free_time=tack_rhs[i]
                )

                results.append(result)
            
            self.repository.add_results(results)

    def get_available_samples(self):
        samples = self.repository.get_available_samples()

        return [
            {
                "sample_id": sample["sample_id"],
                "afterstorage_id": sample["afterstorage_id"],
                "display_name": sample["display_name"],
                "product_name": sample["product_name"]
            }
            for sample in samples
        ]