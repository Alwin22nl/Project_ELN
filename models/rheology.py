from dataclasses import dataclass
from typing import Optional

@dataclass
class Rheologyresult:
    sample_id: str
    afterstorage_id: Optional[str]
    operator_id: int
    remark: str
    yieldstress: str
    vis_at_1: str
    vis_at_5: str
    vis_at_10: str
    humidity: str