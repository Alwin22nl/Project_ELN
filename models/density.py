from dataclasses import dataclass

@dataclass
class DensityResult:
    sample_id : str
    remark : str
    operator_id : str

    vessel_empty : float
    vessel_full : float
    vessel_volume : float

    def calculate_density(self):
        return ((self.vessel_full - self.vessel_empty) / self.vessel_volume)
