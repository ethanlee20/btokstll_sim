
from dataclasses import dataclass

from .util import Interval


@dataclass(frozen=True)
class WC_Set:
    d_c_7: float
    d_c_9: float
    d_c_10: float


@dataclass(frozen=True)
class Uniform_WC_Distribution:
    d_c_7: Interval 
    d_c_9: Interval 
    d_c_10: Interval 