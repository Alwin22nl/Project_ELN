import calendar
import re

from datetime import date

class OverviewService:
    def __init__(self, repository):
        self.repository = repository

    def build_columns(self, required_tests):
        columns = [
            ("Batch", "batch_nr"),
            ("Production", "prod_date")
        ]

        as_columns = []

        if 1 in required_tests:
            columns.extend([
                ("Yield Stress", "yield_stress"),
                ("Vis @10", "vis_at_10")
            ])

            as_columns.extend([
                ("Yield Stress (AS)", "yield_stress_as"),
                ("Vis @10 (AS)", "vis_at_10_as")
            ])

        if 8 in required_tests:
            columns.append(
                ("Initial Tack", "initial_tack")
            )

        if 9 in required_tests:
            columns.extend([
                ("Tack Free", "tack_free_time"),
                ("Skin Formation", "skinformation_time")
            ])

            as_columns.extend([
                ("Tack Free (AS)", "tack_free_time_as"),
                (
                    "Skin Formation (AS)",
                    "skinformation_time_as"
                )
            ])

        if 2 in required_tests:
            columns.extend([
                ("Day 1", "day_1"),
                ("Day 7", "day_7")
            ])

            as_columns.extend([
                ("Day 1 (AS)", "day_1_as"),
                ("Day 7 (AS)", "day_7_as")
            ])

        if 3 in required_tests:
            columns.append(
                ("Shore A", "shore_a_avg")
            )

        if 5 in required_tests:
            columns.extend([
                ("Tmax", "t_max"),
                ("Emax", "e_max")
            ])

        if 4 in required_tests:
            columns.append(
                ("Density", "density_product")
            )

        if 6 in required_tests:
            columns.append(
                ("Adhesion", "adhesion")
            )

        if 7 in required_tests:
            columns.append(
                ("EPDM Adhesion", "epdm_adhesion")
            )

        return columns, as_columns

    def parse_partion_date(self, value):
        if not value:
            return None, None

        value = value.strip()

        match = re.match(
            r"^(\d{1,2})-(\d{1,2})-(\d{4})$",
            value
        )

        if match:
            day = int(match.group(1))
            month = int(match.group(2))
            year = int(match.group(3))

            try:
                parsed = date(
                    year,
                    month,
                    day
                )

                return parsed, parsed

            except ValueError:
                return None, None


        match = re.match(
            r"^(\d{1,2})-(\d{4})$",
            value
        )

        if match:
            month = int(match.group(1))
            year = int(match.group(2))

            try:
                last_day = calendar.monthrange(
                    year,
                    month
                )[1]

                return (
                    date(year, month, 1),
                    date(year, month, last_day)
                )

            except ValueError:
                return None, None


        if re.match(r"^\d{4}$", value):
            year = int(value)

            return (
                date(year, 1, 1),
                date(year, 12, 31)
            )

        return None, None       

    def calculate_averages(self, results, columns, as_columns):
        averages = {}

        for title, field in columns + as_columns:

            values = []

            for row in results:

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

    def get_overview(self, product_id, batch_nr="", prod_date_from="", prod_date_to=""):
        products = self.repository.get_products()

        if not product_id:
            return {
                "products": products,
                "selected_product": None,
                "columns": [],
                "as_columns": [],
                "results": [],
                "batch_nr": "",
                "prod_date_from": "",
                "prod_date_to": "",
                "averages": {}
            }

        required_tests = (
            self.repository.get_required_tests(
                product_id
            )
        )

        columns, as_columns = self.build_columns(
            required_tests
        )

        from_start, from_end = self.parse_partion_date(
            prod_date_from
        )

        to_start, to_end = self.parse_partion_date(
            prod_date_to
        )

        date_from = from_start 
        date_to = to_end

        results = self.repository.get_results(
            product_id=product_id,
            batch_nr=batch_nr,
            date_from=date_from,
            date_to=date_to
        )

        averages = self.calculate_averages(
            results,
            columns,
            as_columns
        )

        return {
            "products": products,
            "selected_product": product_id,
            "columns": columns,
            "as_columns": as_columns,
            "results": results,
            "batch_nr": batch_nr,
            "prod_date_from": prod_date_from,
            "prod_date_to": prod_date_to,
            "averages": averages
        }

    def get_result_details(
            self,
            sample_id,
            test_type,
            afterstorage=False
    ):
        if test_type == "rheology":
            return self.repository.get_rheology_details(sample_id, afterstorage)

        if test_type == "shore_a":
            return self.repository.get_shore_a_details(sample_id)

        if test_type == "initial_tack":
            return self.repository.get_initial_tack_details(sample_id)

        if test_type == "tack_free":
            return self.repository.get_tack_free_details(sample_id, afterstorage)

        if test_type == "skinformation":
            return self.repository.get_skinformation_details(sample_id, afterstorage)

        if test_type == "curabilityday1":
            return self.repository.get_curabilityday1_details(sample_id, afterstorage)

        if test_type == "curabilityday7":
            return self.repository.get_curabilityday7_details(sample_id, afterstorage)

        if test_type == "density":
            return self.repository.get_density_details(sample_id)

        return {}