from models.epdm_adhesion import EpdmAdhesionPrep, EpdmAdhesionTest

class EpdmService:
    def __init__(self, repository):
        self.repository = repository

    def submit_prep_result(self, form, operator_id):
        result = EpdmAdhesionPrep(
            sample_id=form["sample_id"],
            operator_id=operator_id,
            remark=form["remark"],
        )
        self.repository.add_epdm_adhesion_prep(result)

    def submit_test_result(self, form, operator_id):
        result = EpdmAdhesionTest(
            sample_id=form["sample_id"],
            operator_id=operator_id,
            remark=form["remark"],
            europees=form["europees"],
            trc=form["trc"],
            carlisle=form["carlisle"],
            rubber=form["rubber"],
            copper=form["copper"],
            wood=form["wood"],
            aluminium=form["aluminium"],
            aluminium_anod=form["aluminium_anod"],
            lead=form["lead"],
            rvs=form["rvs"],
            concrete=form["concrete"],
            glass=form["glass"],
            pvc=form["pvc"],
            pmma=form["pmma"],
            pc=form["pc"],            
        )
        self.repository.submit_test_results(result)

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
        