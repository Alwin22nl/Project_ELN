from dataclasses import dataclass

@dataclass
class TensilePrep:
    sample_id: str
    operator_id: int
    remark: str

class TensileMeasure:
    sample_id: str
    specimen_no: int
    remark: str

    width1: float
    width2: float
    width3: float

    thickness1: float
    thickness2: float
    thickness3: float

    def calculate_width_avg(self):
        return ((self.width1 + self.width2 + self.width3) / 3)

    def calculate_thickness_avg(self):
        return ((self.thickness1 + self.thickness2 + self.thickness3) / 3)

class TensileTest:
    specimen_id: int
    remark: str
    
    t_50: float
    t_100: float
    t_max: float
    e_max: float