from models.tensile import TensilePrep, TensileMeasure, TensileTest

class TensileService:
    def __init__(self, repository):
        self.repository = repository

    def submit_prep_result(self, form, operator_id):

        result = TensilePrep(
            sample_id=form["sample_id"],
            operator_id=operator_id,
            remark=form["remark"]
        )
        self.repository.add_prep_result(result)

    def submit_measurements(self, form):

        sample_id = form["sample_id"]
        specimen_numbers = form.getlist("specimen_no[]")

        width_1 = form.getlist("width_1[]")
        width_2 = form.getlist("width_2[]")
        width_3 = form.getlist("width_3[]")

        thickness_1 = form.getlist("thickness_1[]")
        thickness_2 = form.getlist("thickness_2[]")
        thickness_3 = form.getlist("thickness_3[]")

        specimens = []

        for i in range(len(specimen_numbers)):
            specimen = TensileMeasure(
                sample_id=sample_id,
                specimen_no=int(specimen_numbers[i]),

                width_1=float(width_1[i]),
                width_2=float(width_2[i]),
                width_3=float(width_3[i]),


                thickness_1=float(thickness_1[i]),
                thickness_2=float(thickness_2[i]),
                thickness_3=float(thickness_3[i]),
            )

            specimens.append(specimen)

        self.repository.add_speciments(specimens)

    def submit_test_result(self, form, operator_id):
        sample_id = form["sample_id"]
        specimen_ids = form.getlist("specimen_id[]")
        remarks = form.getlist("remark[]")

        t_50s = form.getlist("t_50[]")
        t_100s = form.getlist("t_100[]")
        t_maxs = form.getlist("t-max[]")
        e_maxs = form.getlist("e_max[]")

        results = []

        for i in range(len(specimen_ids)):

            result = TensileTest(
                specimen_id=int(specimen_ids[i]),
                remark=remarks[i] if i < len(remarks) else "",

                t_50=float(t_50s[i]),
                t_100=float(t_100s[i]),
                t_max=float(t_maxs[i]),
                e_max=float(e_maxs[i],)
            )

            results.append(result)

        self.repository.complete_test(
            sample_id,
            operator_id,
            results
        )

    def get_prep_overview(self):
        products = self.repository.get_required_products()
        results = self.repository.get_prep_list()

        return products, results

    def get_test_overview(self):
        products = self.repository.get_required_products()
        results = self.repository.get_latest_results()

        return products, results

    def get_samples_for_prep(self):
        samples = self.repository.get_samples_for_prep()

        return [
            {
                "sample_id": sample["sample_id"],
                "batch_nr": sample["batch_nr"]
            }
            for sample in samples
        ]

    def get_samples_for_measurement(self):
        samples = self.repository.get_samples_for_measurement()

        return [
            {
                "sample_id": sample["sample_id"],
                "batch_nr": sample["batch_nr"] 
            }
            for sample in samples
        ]

    def get_samples_for_test(self):
        samples = self.repository.get_samples_for_test()

        return [
            {
                "sample_id": sample["sample_id"],
                "batch_nr": sample["batch_nr"]
            }
            for sample in samples
        ]