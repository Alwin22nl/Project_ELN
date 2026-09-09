from dataclasses import dataclass

@dataclass
class AdhesionPrep:
    sample_id: str
    operator_id: int
    remark: str

@dataclass
class AdhesionTest:
    sample_id: str
    operator_id: int
    remark: str
    rubber: float
    copper: float
    wood: float
    aluminium: float
    aluminium_anod: float
    lead: float
    rvs: float
    concrete: float
    glass: float
    pvc: float
    pmma: float
    pc: float