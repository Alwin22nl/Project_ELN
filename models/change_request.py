from dataclasses import dataclass

@dataclass
class ChangeRequest:
    def __init__(
            self,
            requested_by,
            table_name,
            record_id,
            field_name,
            old_value,
            new_value,
            reason
    ):
        self.requested_by = requested_by
        self.table_name = table_name
        self.record_id = record_id
        self.field_name = field_name
        self.old_value = old_value
        self.new_value = new_value
        self.reason = reason