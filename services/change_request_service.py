from models.change_request import ChangeRequest

class ChangeRequestService:
    def __init__(self, repository):
        self.repository = repository

    def create_request(
            self,
            requested_by,
            table_name,
            record_id,
            field_name,
            old_value,
            new_value,
            reason
    ):
        if not reason.stip():
            raise ValueError("Een reden voor de wijziging is verplicht!")

        if str(old_value) == str(new_value):
            raise ValueError("De nieuwe waarde is hetzelfde als de huisige waarde!")

        change_request = ChangeRequest(
            requested_by=requested_by,
            table_name=table_name,
            record_id=record_id,
            field_name=field_name,
            old_value=old_value,
            new_value=new_value,
            reason=reason
        )

        self.repository.create_request(change_request)