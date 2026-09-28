from dataclasses import dataclass

@dataclass
class ChangeRequest:
    requested_by: int
    table_name: str
    record_id: int
    field_name: str
    old_value: str
    new_value: str
    reason: str