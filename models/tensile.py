from dataclasses import dataclass

@dataclass
class TensilePrep:
    sample_id: str
    operator_id: int
    remark: str

@dataclass
class TensileMeasure:
    sample_id: str
    specimen_no: int

    width_1: float
    width_2: float
    width_3: float

    thickness_1: float
    thickness_2: float
    thickness_3: float

    def calculate_width_avg(self):
        return ((self.width_1 + self.width_2 + self.width_3) / 3)

    def calculate_thickness_avg(self):
        return ((self.thickness_1 + self.thickness_2 + self.thickness_3) / 3)

@dataclass
class TensileTest:
    specimen_id: int
    remark: str

    t_50: float
    t_100: float
    t_max: float
    e_max: float