from decimal import Decimal, InvalidOperation
from config.limit_result_config import LIMIT_RESULT_CONFIG

class LimitEvaluationService:
    def __init__(self, limits_service):
        self.limits_service = limits_service

    @staticmethod
    def to_decimal(value):
        if value is None or value == "":
            return None

        try:
            number = Decimal(str(value).strip())
        except (InvalidOperation, ValueError):
            raise ValueError(
                f"ongeldige meetwaarde {value}"
            )

        if not number.is_finite():
            raise ValueError(
                "Meetwaarden moeten eindige getallen zijn."
            )

        return number

    def evaluate_result(
            self,
            product_id,
            test_key,
            field_name,
            value,
            test_stage="initial"
    ):
        limit = self.limits_service.get_active_limit(
            product_id=product_id,
            test_key=test_key,
            field_name=field_name,
            test_stage=test_stage
        )

        measured_value = self.to_decimal(value)

        if limit is None:
            return {
                "field_name": field_name,
                "value": measured_value,
                "limit_id": None,
                "min_value": None,
                "max_value": None,
                "status": "no_limit"
            }

        minimum = self.to_decimal(limit["min_value"])
        maximum = self.to_decimal(limit["max_value"])

        if measured_value is None:
            status = "not_evaluated"

        elif (minimum is not None and measured_value < minimum):
            status = "outside"

        elif (maximum is not None and measured_value > maximum):
            status = "outside"

        else:
            status = "within"

        return {
            "field_name": field_name,
            "value": measured_value,
            "limit_id": limit["limit_id"],
            "min_value": minimum,
            "max_value": maximum,
            "status": status
        }

    def evaluate_test(
            self,
            product_id,
            test_key,
            results,
            test_stage="initial"
    ):
        config = LIMIT_RESULT_CONFIG.get(test_key)

        if config is None:
            raise ValueError(
                f"Onbekende test: {test_key}"
            )

        evaluations = {}

        for field_name in config["fields"]:
            value = results.get(field_name)
            evaluations[field_name] = (
                self.evaluate_result(
                    product_id=product_id,
                    test_key=test_key,
                    field_name=field_name,
                    value=value,
                    test_stage=test_stage
                )
            )

        return evaluations

    def calculate_tensile_averages(
            self,
            specimens
    ):
        config = LIMIT_RESULT_CONFIG["tensile"]

        expected_count = config.get("expected_specimens", 4)

        fields = config["fields"]

        averages = {
            field_name: None
            for field_name in fields
        }

        if len(specimens) != expected_count:
            return averages

        valid_specimens = []

        for specimen in specimens:
            remark = specimen.get("remark")

            if (remark is not None and str(remark).strip()):
                continue

            valid_specimens.append(specimen)

        if not valid_specimens:
            return averages

        for field_name in fields:
            values = []
            incomplete = False

            for specimen in valid_specimens:
                value = self.to_decimal(specimen.get(field_name))
                if value is None:
                    incomplete = True
                    break

                values.append(value)

            if incomplete:
                continue

            averages[field_name] = (
                sum(values) / Decimal(len(values))
            )

        return averages