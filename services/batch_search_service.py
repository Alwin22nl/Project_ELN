class BatchSearchService:

    def __init__(self, repository):
        self.repository = repository

    def search_batch(self, batch_nr):

        batches = self.repository.get_batch_group(
            batch_nr
        )

        if not batches:
            return None, [], [], []

        sample_ids = [
            batch["sample_id"]
            for batch in batches
        ]

        batch_by_sample = {
            batch["sample_id"]: batch["batch_nr"]
            for batch in batches
        }

        product_ids = {
            batch["product_id"]
            for batch in batches
        }

        required_tests = set()

        for product_id in product_ids:
            required_tests.update(
                self.repository.get_required_tests(
                    product_id
                )
            )

        results = []

        if 1 in required_tests:
            self._add_rheology(
                results,
                sample_ids
            )

        if 8 in required_tests:
            self._add_initial_tack(
                results,
                sample_ids
            )

        if 9 in required_tests:
            self._add_skinformation(
                results,
                sample_ids
            )

        if 4 in required_tests:
            self._add_density(
                results,
                sample_ids
            )

        if 3 in required_tests:
            self._add_shore_a(
                results,
                sample_ids
            )

        if 2 in required_tests:
            self._add_curability(
                results,
                sample_ids
            )

        if 5 in required_tests:
            self._add_tensile(
                results,
                sample_ids
            )

        if 6 in required_tests:
            self._add_adhesion(
                results,
                sample_ids,
                batch_by_sample
            )

        if 7 in required_tests:
            self._add_epdm_adhesion(
                results,
                sample_ids,
                batch_by_sample
            )

        remarks = []

        for batch in batches:
            remark = batch.get("remark")
            if remark:
                remarks.append({
                    "sample_id":
                        batch["sample_id"],

                    "batch_nr":
                        batch["batch_nr"],

                    "remark":
                        remark
                })

        product_names = sorted({
            batch["product_name"]
            for batch in batches
        })

        batch_summary = {
            "sample_id":
                batches[0]["sample_id"],

            "batch_nr":
                batch_nr,

            "prod_date":
                batches[0]["prod_date"],

            "product_id":
                batches[0]["product_id"],

            "product_name":
                " / ".join(product_names),

            "remark":
                None,

            "matched_count":
                len(batches)
        }

        return (
            batch_summary,
            batches,
            results,
            remarks
        )

    def _average_rows(
        self,
        rows,
        fields
    ):
        averages = {}

        for field in fields:
            values = []
            for row in rows:
                value = row.get(field)

                if value is None:
                    continue

                try:
                    values.append(
                        float(value)
                    )

                except (TypeError, ValueError):
                    continue

            if values:
                averages[field] = round(
                    sum(values) / len(values),
                    3
                )

            else:
                averages[field] = None

        return averages

    def _contains_result(self, values):
        return any(
            value is not None
            for value in values.values()
        )

    def _result(
        self,
        test_name,
        values
    ):
        return {
            "test_name": test_name,
            "operator": "",
            "test_date": "",
            "values": values
        }


    def _no_result(self, test_name):
        return {
            "test_name": test_name,
            "operator": "",
            "test_date": "",
            "values": {
                "Status": "No result recorded"
            }
        }

    def _add_rheology(
        self,
        results,
        sample_ids
    ):

        normal_rows = self.repository.get_rheology(
            sample_ids,
            afterstorage=False
        )

        as_rows = self.repository.get_rheology(
            sample_ids,
            afterstorage=True
        )


        normal = self._average_rows(
            normal_rows,
            [
                "yield_stress",
                "vis_at_1",
                "vis_at_5",
                "vis_at_10",
                "humidity"
            ]
        )

        afterstorage = self._average_rows(
            as_rows,
            [
                "yield_stress",
                "vis_at_1",
                "vis_at_5",
                "vis_at_10",
                "humidity"
            ]
        )

        if self._contains_result(normal):

            results.append(
                self._result(
                    "Rheology",
                    {
                        "Yield stress": normal["yield_stress"],
                        "Viscosity @1": normal["vis_at_1"],
                        "Viscosity @5": normal["vis_at_5"],
                        "Viscosity @10": normal["vis_at_10"],
                        "Humidity": normal["humidity"]
                    }
                )
            )

        if self._contains_result(afterstorage):
            results.append(
                self._result(
                    "Rheology (after storage)",
                    {
                        "Yield stress": afterstorage["yield_stress"],
                        "Viscosity @1": afterstorage["vis_at_1"],
                        "Viscosity @5": afterstorage["vis_at_5"],
                        "Viscosity @10": afterstorage["vis_at_10"],
                        "Humidity": afterstorage["humidity"]
                    }
                )
            )

        if (
            not self._contains_result(normal)
            and
            not self._contains_result(afterstorage)
        ):
            results.append(
                self._no_result(
                    "Rheology"
                )
            )

    def _add_initial_tack(
        self,
        results,
        sample_ids
    ):

        rows = self.repository.get_initial_tack(
            sample_ids
        )

        averages = self._average_rows(
            rows,
            [
                "initial_tack",
                "humidity"
            ]
        )

        if not self._contains_result(averages):
            results.append(
                self._no_result(
                    "Initial Tack"
                )
            )
            return

        results.append(
            self._result(
                "Initial Tack",
                {
                    "Initial tack": averages["initial_tack"],
                    "Humidity": averages["humidity"]
                }
            )
        )

    def _add_skinformation(
        self,
        results,
        sample_ids
    ):

        normal_rows = (
            self.repository.get_skinformation(
                sample_ids,
                afterstorage=False
            )
        )

        as_rows = (
            self.repository.get_skinformation(
                sample_ids,
                afterstorage=True
            )
        )

        normal = self._average_rows(
            normal_rows,
            [
                "tack_free_time",
                "skinformation_time"
            ]
        )

        afterstorage = self._average_rows(
            as_rows,
            [
                "tack_free_time",
                "skinformation_time"
            ]
        )

        if self._contains_result(normal):

            results.append(
                self._result(
                    "Skinformation",
                    {
                        "Tack free":
                            normal["tack_free_time"],

                        "Skinformation":
                            normal["skinformation_time"]
                    }
                )
            )

        if self._contains_result(afterstorage):
            results.append(
                self._result(
                    "Skinformation (after storage)",
                    {
                        "Tack free":
                            afterstorage["tack_free_time"],

                        "Skinformation":
                            afterstorage[
                                "skinformation_time"
                            ]
                    }
                )
            )

        if (
            not self._contains_result(normal)
            and
            not self._contains_result(afterstorage)
        ):
            results.append(
                self._no_result(
                    "Skinformation"
                )
            )

    def _add_density(
        self,
        results,
        sample_ids
    ):

        rows = self.repository.get_density(
            sample_ids
        )

        averages = self._average_rows(
            rows,
            ["density_product"]
        )

        if not self._contains_result(averages):
            results.append(
                self._no_result(
                    "Density"
                )
            )
            return

        results.append(
            self._result(
                "Density",
                {
                    "Density": averages["density_product"]
                }
            )
        )

    def _add_shore_a(
        self,
        results,
        sample_ids
    ):

        rows = self.repository.get_shore_a(
            sample_ids
        )

        averages = self._average_rows(
            rows,
            [
                "shore_a_avg",
                "temperature",
                "humidity"
            ]
        )

        if not self._contains_result(averages):
            results.append(
                self._no_result(
                    "Shore A"
                )
            )
            return

        results.append(
            self._result(
                "Shore A",
                {
                    "Average": averages["shore_a_avg"],
                    "Temperature": averages["temperature"],
                    "Humidity": averages["humidity"]
                }
            )
        )

    def _add_curability(
        self,
        results,
        sample_ids
    ):

        normal_rows = self.repository.get_curability(
            sample_ids,
            afterstorage=False
        )

        as_rows = self.repository.get_curability(
            sample_ids,
            afterstorage=True
        )

        normal = self._average_rows(
            normal_rows,
            [
                "day_1",
                "day_7"
            ]
        )

        afterstorage = self._average_rows(
            as_rows,
            [
                "day_1",
                "day_7"
            ]
        )

        if self._contains_result(normal):
            results.append(
                self._result(
                    "Curability",
                    {
                        "24h": normal["day_1"],
                        "7d": normal["day_7"]
                    }
                )
            )

        if self._contains_result(afterstorage):

            results.append(
                self._result(
                    "Curability (after storage)",
                    {
                        "24h": afterstorage["day_1"],
                        "7d": afterstorage["day_7"]
                    }
                )
            )

        if (
            not self._contains_result(normal)
            and
            not self._contains_result(afterstorage)
        ):
            results.append(
                self._no_result(
                    "Curability"
                )
            )

    def _add_tensile(
        self,
        results,
        sample_ids
    ):

        sample_averages = (
            self.repository
            .get_tensile_sample_averages(
                sample_ids
            )
        )

        averages = self._average_rows(
            sample_averages,
            [
                "t_50",
                "t_100",
                "t_max",
                "e_max"
            ]
        )

        if not self._contains_result(averages):
            results.append(
                self._no_result(
                    "Tensile"
                )
            )
            return

        results.append(
            self._result(
                "Tensile",
                {
                    "T50": averages["t_50"],
                    "T100": averages["t_100"],
                    "Tmax": averages["t_max"],
                    "Emax": averages["e_max"]
                }
            )
        )

    def _add_adhesion(
        self,
        results,
        sample_ids,
        batch_by_sample
    ):

        rows = self.repository.get_adhesion(
            sample_ids
        )

        if not rows:
            results.append(
                self._no_result(
                    "Adhesion"
                )
            )
            return

        for row in rows:
            batch_nr = batch_by_sample.get(
                row["sample_id"],
                ""
            )

            results.append(
                self._result(
                    f"Adhesion - {batch_nr}",
                    {
                        "Rubber":row["rubber"],
                        "Copper": row["copper"],
                        "Wood": row["wood"],
                        "Aluminium": row["aluminium"],
                        "Aluminium Anod.": row["aluminium_anod"],
                        "Lead": row["lead"],
                        "RVS": row["rvs"],
                        "Concrete": row["concrete"],
                        "Glass": row["glass"],
                        "PVC": row["pvc"],
                        "PMMA": row["pmma"],
                        "PC": row["pc"]
                    }
                )
            )

    def _add_epdm_adhesion(
        self,
        results,
        sample_ids,
        batch_by_sample
    ):

        rows = self.repository.get_epdm_adhesion(
            sample_ids
        )

        if not rows:
            results.append(
                self._no_result(
                    "EPDM Adhesion"
                )
            )
            return

        for row in rows:
            batch_nr = batch_by_sample.get(
                row["sample_id"],
                ""
            )

            results.append(
                self._result(
                    f"EPDM Adhesion - {batch_nr}",
                    {
                        "Eu-EPDM": row["europees"],
                        "TRC-EPDM": row["trc"],
                        "CL-EPDM": row["carlisle"],
                        "Rubber": row["rubber"],
                        "Copper": row["copper"],
                        "Wood": row["wood"],
                        "Aluminium": row["aluminium"],
                        "Aluminium Anod.": row["aluminium_anod"],
                        "Lead": row["lead"],
                        "RVS": row["rvs"],
                        "Concrete": row["concrete"],
                        "Glass": row["glass"],
                        "PVC": row["pvc"],
                        "PMMA": row["pmma"],
                        "PC": row["pc"]
                    }
                )
            )