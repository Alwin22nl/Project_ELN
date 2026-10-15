class LimitFlagService:
    def __init__(self, flag_repository, notification_service):
        self.flag_repository = flag_repository
        self.notification_service = notification_service

    def process_evaluations(
            self,
            sample_id,
            test_key,
            evaluations,
            test_stage="initial"
    ):
        changes = []

        for field_name, evaluation in evaluations.itmes():
            status = evaluations["status"]

            if evaluation["field_name"] != field_name:
                raise ValueError(
                    "Resultaatveld komt niet overeen "
                    "met de evaluatie."
                )

            if status == "outside":
                result = self.flag_repository.open_or_update_flag(
                    sample_id=sample_id,
                    test_key=test_key,
                    test_stage=test_stage,
                    evaluation=evaluation
                )
                
                flag_id = result["flag_id"]

                if result["created"]:
                    self.create_flag_notifications(flag_id)

                changes.append({
                    "field": field_name,
                    "action": (
                        "created"
                        if result["created"]
                        else "updated"
                    ),
                    "flag_id": flag_id
                })

            elif status == "within":
                resolved_id = self.flag_repository.resolve_flag(
                    sample_id=sample_id,
                    test_key=test_key,
                    field_name=field_name,
                    test_stage=test_stage
                )

                if resolved_id is not None:
                    self.notification_service.close_limit_flag_notifications(resolved_id)

                    changes.append({
                        "field": field_name,
                        "action": "resolved",
                        "flag_id": flag_id
                    })

            elif status in ("not_evaluated", "no_limit"):
                continue

            else:
                raise ValueError(
                    f"Onbekende evaluatie status: {status}"
                )

        return changes

    def create_flag_notifications(self, flag_id):
        users = self.notification_service.get_limit_notifications_recipients()

        for user in users:
            self.notification_service.create_notification(
                user_id=user["user_id"],
                notification_type="limit_exceeded",
                title="Limietoverschrijding",
                message="1 of meerdere batches hebben een meetresultaat buiten de gestelde limieten",
                reference_type="limit_flag",
                reference_id=flag_id,
                link="/limits/exceedances"
            )