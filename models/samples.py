from dataclasses import dataclass
from datetime import date

@dataclass
class Samples:
    batch_nr: str
    prod_date: date
    product_id: int
    afterstorage_required: bool
    remark: str