from dataclasses import dataclass


@dataclass
class SimulationMessage:
    success: str = 'Simulation will be execute'
    internal_error: str = 'Simulation has invalid codification'


@dataclass
class GoogleMessage:
    unavailable: str = 'Unavailable'

