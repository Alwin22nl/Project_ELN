from dataclasses import dataclass
from typing import Optional

@dataclass
class skinformationresult:
    sample_id: str
    afterstorage_id: Optional[str]
    operator_id: int
    remark: str
    skinformation_time = str
    temp_skinformation_time: str
    rh_skinformation_time: str
    tack_free_time: str
    temp_tack_free_time: str
    rh_tack_free_time: str