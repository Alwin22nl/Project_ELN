from dataclasses import dataclass

@dataclass
class EpdmAdhesionPrep:
    sample_id: str
    operator_id: int
    remark: str

@dataclass
class EpdmAdhesionTest:
    sample_id: str
    operator_id: int
    remark: str
    europees: float
    trc: float
    carlisle: float
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