# models.py

from dataclasses import dataclass
from typing import Optional


@dataclass
class StopPuck:
    """
    Represents one physical stop puck.

    The puck prevents a spring from compressing below a calculated minimum length.

    minimum spring length =
        puck thickness + top offset + bottom offset
    """

    thickness: float
    top_offset: float
    bottom_offset: float

    def minimum_spring_length(self) -> float:
        return self.thickness + self.top_offset + self.bottom_offset


@dataclass
class BlankCoupler:
    """
    Non-compressing spacer/coupler between springs.
    """

    name: str
    length: float


@dataclass
class Spring:
    """
    Linear spring.

    max_compression is no longer manually entered.
    It is calculated from stop puck geometry if a stop puck is provided.
    """

    name: str
    rate: float
    free_length: float
    stop_puck: Optional[StopPuck] = None

    def max_compression(self) -> Optional[float]:
        if self.stop_puck is None:
            return None

        max_comp = self.free_length - self.stop_puck.minimum_spring_length()

        # Prevent negative compression if invalid geometry is entered
        return max(0.0, max_comp)


@dataclass
class SpringResult:
    name: str
    rate: float
    free_length: float
    compression: float
    compressed_length: float
    max_compression: Optional[float]
    stopped: bool


@dataclass
class StackResult:
    applied_force: float
    preload_turns: float
    adjuster_pitch: float
    preload_displacement: float
    preload_force: float
    total_force: float

    total_spring_compression: float
    total_spring_length: float
    total_coupler_length: float
    calculated_collar_length: float

    measured_collar_length: Optional[float]
    collar_length_error: Optional[float]

    spring_results: list[SpringResult]


@dataclass
class SpringStack:
    """
    Three-spring system with two blank couplers.

    Physical order:
        Collar
        Spring 1
        Coupler 1
        Spring 2
        Coupler 2
        Spring 3
        Collar
    """

    spring_1: Spring
    coupler_1: BlankCoupler
    spring_2: Spring
    coupler_2: BlankCoupler
    spring_3: Spring
    measured_collar_length: Optional[float] = None

    def springs(self) -> list[Spring]:
        return [self.spring_1, self.spring_2, self.spring_3]

    def couplers(self) -> list[BlankCoupler]:
        return [self.coupler_1, self.coupler_2]

    def total_coupler_length(self) -> float:
        return self.coupler_1.length + self.coupler_2.length

    def free_spring_length(self) -> float:
        return sum(spring.free_length for spring in self.springs())

    def free_collar_length(self) -> float:
        return self.free_spring_length() + self.total_coupler_length()