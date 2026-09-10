from dataclasses import dataclass
from typing import Optional

@dataclass
class CurabilityPrep:
    sample_id: str
    operator_id: int
    remark: str

@dataclass
class CurabilityTest: 
    sample_id: str
    afterstorage_id: Optional[str]
    operator_id: int
    remark: str

    day_1 = float
    temp_day1: float
    rh_day1: float

    day_7: float
    temp_day7: float
    rh_day7: float

