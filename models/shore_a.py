from dataclasses import dataclass

@dataclass
class ShoreATestResult:
    sample_id : str
    operator_id : int
    remark : str
    shore_a_1 : float
    shore_a_2 : float
    shore_a_3 : float
    temperature : str
    humidity: str

    def calculate_avg_shore_a(self):
        return round((self.shore_a_1 + self.shore_a_2 + self.shore_a_3) / 3)
@dataclass    
class ShoreAPrepResult:
    sample_id : str
    operator_id : int
    remark : str
