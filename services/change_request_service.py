from models.change_request import ChangeRequest


TEST_TABLES = {
    "rheology": "rheology",
    "skinformation": "skinformation",
    "curability": "curability",
    "density": "density",
    "initial_tack": "initial_tack",
    "shore_a": "shore_a",
    "tensile_strength": "tensile_strength",
    "adhesion": "adhesion",
    "epdm_adhesion": "epdm_adhesion"
}

from models.change_request import ChangeRequest


TEST_CONFIG = {
    "rheology": {
        "label": "Rheology",
        "table": "rheology",

        "id_column": "rheology_id",

        "fields": {
            "yield_stress": "Yield stress",
            "vis_at_1": "Viscositeit @ 1",
            "vis_at_5": "Viscositeit @ 5",
            "vis_at_10": "Viscositeit @ 10",
            "humidity": "Luchtvochtigheid",
            "remark": "Opmerking"
        }
    }
}


class ChangeRequestService:
    def __init__(self, repository):
        self.repository = repository

    def create_request(self, form, requested_by):

        sample_id = int(form["sample_id"])
        test_key = form["test_target"]
        record_id = int(form["record_id"])
        field_name = form["field_name"]

        new_value = form["new_value"]
        reason = form["reason"]

        if test_key not in TEST_TABLES:
            raise ValueError("Onbekende test.")

        table_name = TEST_TABLES[test_key]

        old_value = self.get_current_value(
            test_key=test_key,
            record_id=record_id,
            field_name=field_name,
            sample_id=sample_id
)

        if str(old_value) == str(new_value):
            raise ValueError(
                "De nieuwe waarde is hetzelfde als de huidige waarde."
            )

        if not reason.strip():
            raise ValueError(
                "Een reden voor de wijziging is verplicht!"
            )

        change_request = ChangeRequest(
            requested_by=requested_by,
            table_name=table_name,
            record_id=record_id,
            field_name=field_name,
            old_value=str(old_value),
            new_value=new_value,
            reason=reason.strip()
        )

        self.repository.create_request(change_request)

    def get_products(self):
        return self.repository.get_products()

    def get_batches(self, product_id):
        return self.repository.get_batches(product_id)

    def get_available_tests(self, sample_id):

        available_tests = []

        for test_key, config in TEST_CONFIG.items():
            records = self.repository.get_test_records(
                table_name=config["table"],
                id_column=config["id_column"],
                sample_id=sample_id
            )

            for record in records:
                label = config["label"]
                if record["afterstorage_id"] is not None:
                    label += " - AS"

                available_tests.append({
                    "test_key": test_key,
                    "record_id": record["record_id"],
                    "label": label
                })

        return available_tests

    def get_changeable_fields(self, test_key, record_id):

        if test_key not in TEST_CONFIG:
            raise ValueError("Onbekende test.")

        config = TEST_CONFIG[test_key]

        field_names = list(
            config["fields"].keys()
        )

        result = self.repository.get_test_fields(
            table_name=config["table"],
            id_column=config["id_column"],
            record_id=record_id,
            field_names=field_names
        )

        if result is None:
            raise ValueError(
                "Het geselecteerde testresultaat bestaat niet."
            )

        fields = []

        for field_name, label in config["fields"].items():

            fields.append({
                "field": field_name,
                "label": label,
                "value": result[field_name]
            })

        return fields

    def get_current_value(
        self,
        test_key,
        record_id,
        field_name,
        sample_id
    ):

        if test_key not in TEST_CONFIG:
            raise ValueError("Onbekende test.")

        config = TEST_CONFIG[test_key]

        if field_name not in config["fields"]:
            raise ValueError(
                "Dit veld mag niet worden gewijzigd."
            )

        value = self.repository.get_current_value(
            table_name=config["table"],
            id_column=config["id_column"],
            record_id=record_id,
            sample_id=sample_id,
            field_name=field_name
        )

        if value is None:
            raise ValueError(
                "Het geselecteerde resultaat kon niet worden gevonden."
            )

        return value

    def get_requests_by_user(self, user_id):
        rows = self.repository.get_requests_by_user(user_id)

        requests = []

        for row in rows:
            item = dict(row)
            item["test_label"] = item["table_name"]
            item["field_label"] = item["field_name"]

            for test_key, config in TEST_CONFIG.items():
                if config["table"] == item["table_name"]:
                    item["test_label"] = config["label"]
                    item["field_label"] = config["fields"].get(
                        item["field_name"],
                        item["field_name"]
                    )
                    break

            requests.append(item)
        return requests