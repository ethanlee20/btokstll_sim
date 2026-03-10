
from random import seed, uniform
from dataclasses import asdict

from .wc_types import Uniform_WC_Distribution, WC_Set


class Sampler:
    def __init__(
        self, 
        dist:Uniform_WC_Distribution,
        seed_:int|None=None,
    ):
        seed(seed_)
        self._dist_items = asdict(dist).items()

    def sample(
        self, 
        n:int,
    ) -> list[WC_Set]:
        return [
            self._sample()
            for _ in range(n)
        ]
    
    def _sample(
        self,
    ) -> WC_Set:
        return WC_Set(
            **{
                wc: uniform(*bounds) 
                for wc, bounds in self._dist_items
            }
        )
