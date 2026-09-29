from models.change_request import ChangeRequest
from config.test import TEST_CONFIG


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

        if test_key not in TEST_CONFIG:
            raise ValueError(
                "Onbekende test."
            )

        config = TEST_CONFIG[test_key]

        table_name = config["table"]

        if field_name not in config["fields"]:
            raise ValueError(
                "Dit veld mag niet worden gewijzigd."
            )

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

        self.repository.create_request(
            change_request
        )

    def get_products(self):
        return self.repository.get_products()

    def get_batches(self, product_id):
        return self.repository.get_batches(
            product_id
        )

    def get_available_tests(self, sample_id):

        available_tests = []

        for test_key, config in TEST_CONFIG.items():

            if config.get("special_type") == "specimens":

                specimens = (
                    self.repository.get_tensile_specimens(
                        sample_id
                    )
                )

                for specimen in specimens:

                    available_tests.append({
                        "test_key": test_key,
                        "record_id": specimen[
                            "specimen_id"
                        ],
                        "label": (
                            f'{config["label"]} - '
                            f'Specimen {specimen["specimen_no"]}'
                        )
                    })

                continue

            records = self.repository.get_test_records(
                table_name=config["table"],
                id_column=config["id_column"],
                sample_id=sample_id,
                has_afterstorage=config[
                    "has_afterstorage"
                ]
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

    def get_changeable_fields(
        self,
        test_key,
        record_id
    ):

        if test_key not in TEST_CONFIG:
            raise ValueError(
                "Onbekende test."
            )

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

        for field_name, label in config[
            "fields"
        ].items():

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
            raise ValueError(
                "Onbekende test."
            )

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

        rows = self.repository.get_requests_by_user(
            user_id
        )

        requests = []

        for row in rows:

            item = dict(row)

            item["test_label"] = item[
                "table_name"
            ]

            item["field_label"] = item[
                "field_name"
            ]

            for test_key, config in TEST_CONFIG.items():

                if (
                    config["table"]
                    == item["table_name"]
                ):

                    item["test_label"] = config[
                        "label"
                    ]

                    item["field_label"] = (
                        config["fields"].get(
                            item["field_name"],
                            item["field_name"]
                        )
                    )

                    break

            requests.append(item)

        return requests

    def get_pending_requests(
        self,
        reviewer_id
    ):

        rows = (
            self.repository.get_pending_requests(
                reviewer_id
            )
        )

        requests = []

        for row in rows:

            item = dict(row)

            item["test_label"] = item[
                "table_name"
            ]

            item["field_label"] = item[
                "field_name"
            ]

            for test_key, config in TEST_CONFIG.items():

                if (
                    config["table"]
                    == item["table_name"]
                ):

                    item["test_label"] = config[
                        "label"
                    ]

                    item["field_label"] = (
                        config["fields"].get(
                            item["field_name"],
                            item["field_name"]
                        )
                    )

                    break

            requests.append(item)

        return requests
    
    def reject_request(
        self,
        change_request_id,
        reviewer_id,
        review_comment
    ):

        if not review_comment.strip():
            raise ValueError(
                "Geef een reden voor het afwijzen "
                "van de aanvraag."
            )

        success = self.repository.review_request(
            change_request_id=change_request_id,
            status="rejected",
            reviewed_by=reviewer_id,
            review_comment=review_comment.strip()
        )

        if not success:
            raise ValueError(
                "Deze aanvraag kan niet worden afgewezen. "
                "Mogelijk is deze al behandeld of is het "
                "je eigen aanvraag."
            )

    def approve_request(
        self,
        change_request_id,
        reviewer_id,
        review_comment=""
    ):

        change = self.repository.get_request(
            change_request_id
        )

        if change is None:
            raise ValueError(
                "Wijzigingsaanvraag bestaat niet."
            )

        if change["status"] != "pending":
            raise ValueError(
                "Deze wijzigingsaanvraag is al behandeld."
            )

        if change["requested_by"] == reviewer_id:
            raise ValueError(
                "Je kunt je eigen wijzigingsaanvraag "
                "niet goedkeuren."
            )

        config = None

        for test_key, test_config in TEST_CONFIG.items():

            if (
                test_config["table"]
                == change["table_name"]
            ):

                config = test_config
                break

        if config is None:
            raise ValueError(
                "Deze test mag niet automatisch "
                "worden gewijzigd."
            )

        if change["field_name"] not in config["fields"]:
            raise ValueError(
                "Dit veld mag niet worden gewijzigd."
            )

        self.repository.approve_and_apply_change(
            change_request_id=change_request_id,
            reviewer_id=reviewer_id,
            table_name=config["table"],
            id_column=config["id_column"],
            field_name=change["field_name"],
            review_comment=review_comment,
            recalculate=config.get(
                "recalculate"
            )
        )