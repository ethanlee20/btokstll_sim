
from dataclasses import dataclass, asdict
from pathlib import Path
from json import load, dump
from types import FunctionType
from functools import cached_property


def load_json(
    path: Path,
)-> dict:
    with open(path, 'r') as f:
        return load(f)


def dump_json(
    obj: dict,
    path: Path,
) -> None:
    with open(path, 'x') as f:
        return dump(
            obj, 
            f, 
            indent=4,
        )


def safer_convert_to_int(
    x:float,
) -> int:
    assert x.is_integer()
    return int(x)


@dataclass
class Interval:
    left:float
    right:float
    
    def __post_init__(
        self
    ):
        if self.left > self.right:
            raise ValueError(
                "Interval left bound must be greater" 
                " than or equal to right bound."
            )
        
    def __iter__(
        self,
    ):
        return (
            self.left, 
            self.right,
        ).__iter__()
    

@dataclass(frozen=True)
class WC_Set:
    d_c_7: float
    d_c_9: float
    d_c_10: float

    def __iter__(self):
        return (
            self.d_c_7,
            self.d_c_9,
            self.d_c_10,
        ).__iter__()


@dataclass(frozen=True)
class Uniform_WC_Dist:
    d_c_7: Interval 
    d_c_9: Interval 
    d_c_10: Interval 

    def __iter__(self):
        return (
            self.d_c_7, 
            self.d_c_9, 
            self.d_c_10,
        ).__iter__()


@dataclass
class Metadata:
    trial_num: int
    num_events: int
    num_subtrials: int
    split: str
    lepton_flavor: str
    wc_set: WC_Set
    wc_dist: Uniform_WC_Dist

    @property
    def num_subtrial_events(
        self,
    ) -> int:
        return safer_convert_to_int(
            self.num_events
            / self.num_subtrials
        )
    
    def to_json_file(
        self, 
        path,
    ) -> None:
        dump_json(
            asdict(self), 
            path,
        )

    @classmethod
    def from_json_file(
        cls, 
        path:Path,
    ):
        dict_ = load_json(path)
        for key, cls_ in zip(
            ["wc_set", "wc_dist"], 
            [WC_Set, Uniform_WC_Dist],
        ):
            dict_[key] = cls_(**dict_[key])
        return cls(**dict_)
    

@dataclass(frozen=True)
class Paths:
    dir_: Path
    metadata_file_name:str = "metadata.json"
    recon_file_name:FunctionType = lambda subtrial: f"recon_{subtrial}.root"
    sim_file_name:FunctionType = lambda subtrial: f"sim_{subtrial}.root"
    decay_file_name:str = "decay.dec"
    log_file_name:str = "log.log"

    @cached_property
    def metadata_file_path(
        self,
    ) -> Path:
        return self.dir_.joinpath(self.metadata_file_name)
    
    def recon_file_path(
        self, 
        subtrial:int|str
    ) -> Path:
        return self.dir_.joinpath(self.recon_file_name(subtrial))
    
    def sim_file_path(
        self, 
        subtrial:int|str,
    ) -> Path:
        return self.dir_.joinpath(self.sim_file_name(subtrial))
    
    @cached_property
    def decay_file_path(
        self,
    ) -> Path:
        return self.dir_.joinpath(self.decay_file_name)
    
    @cached_property
    def log_file_path(
        self,
    ) -> Path:
        return self.dir_.joinpath(self.log_file_name)
    
