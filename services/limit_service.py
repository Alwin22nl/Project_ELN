from config.limit_result_config import LIMIT_RESULT_CONFIG

class LimitsService:
    def __init__(self, repository):
        self.repository = repository

    def validate_limit_target(self, test_key, field_name, test_stage):
        config = LIMIT_RESULT_CONFIG.get(test_key)

        if config is None:
            raise ValueError(
                "ongeldige test geselecteerd."
            )

        if field_name not in config["fields"]:
            raise ValueError(
                "Ongeldige resultaatwaarde geselecteerd."
            )

        if test_stage not in ("initial", "after_storage"):
            raise ValueError(
                "Ongeldig meetmoment geselecteerd"
            )

        if test_stage == "after_storage" and not config["has_afterstorage"]:
            raise ValueError(
                "Deze test heeft geen after-storage meeting."
            )

    def get_product_limits(self, product_id, include_inactivity=False):
        return self.repository.get_product_limits(product_id, include_inactivity)

    def get_active_limit(self, product_id, test_key, field_name, test_stage="initial"):
        self.validate_limit_target(test_key, field_name, test_stage)

        return self.repository.get_active_limit(product_id, test_key, field_name, test_stage)

    def create_limit(self, product_id, test_key, field_name, test_stage, min_value, max_value, created_by):
        self.validate_limit_target(test_key, field_name, test_stage)

        return self.repository.create_limit(
            product_id=product_id,
            test_key=test_key,
            field_name=field_name,
            test_stage=test_stage,
            min_value=min_value,
            max_value=max_value,
            created_by=created_by
        )

    def replace_limit(self, limit_id, min_value, max_value, created_by):
        return self.repository.replace_limit(
            limit_id=limit_id,
            min_value=min_value,
            max_value=max_value,
            created_by=created_by
        )

    def deactivate_limit(self, limit_id):
        return self.repository.deactivate_limit(limit_id)

    def get_available_tests(self):
        return LIMIT_RESULT_CONFIG