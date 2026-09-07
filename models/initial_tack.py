from dataclasses import dataclass

@dataclass
class InitialTackResult:
    sample_id : str
    remark : str
    operator_id : int

    area : float
    area_weight : float
    added_weight : float
    humidity : str


    def calculate_initial_tack(self):
        return ((self.area_weight + self.added_weight) / self.area)
