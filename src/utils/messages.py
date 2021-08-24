from dataclasses import dataclass


@dataclass
class SimulationMessage:
    success: str = 'Simulation has been executed'
