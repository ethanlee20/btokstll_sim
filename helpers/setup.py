
from dataclasses import dataclass, astuple, asdict
from pathlib import Path
from functools import cached_property
from json import load

from .wc_types import Uniform_WC_Distribution, WC_Set
from .config import metadata_file_name
from .util import safer_convert_to_int, dump_json


@dataclass(frozen=True)
class Trial_Metadata:
    trial_num: int
    num_events: int
    num_subtrials: int
    split: str
    lepton_flavor: str
    wc_set: WC_Set
    wc_dist: Uniform_WC_Distribution

    @cached_property
    def num_events_per_subtrial(
        self,
    ):
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


def _make_metadatas(
    num_trials,
    wc_samples:list[WC_Set],
    num_events_per_trial:int,
    num_subtrials:int,
    split:str,
    lepton_flavor:str,
    wc_dist:Uniform_WC_Distribution,
) -> list[Trial_Metadata]:
    if num_trials != len(wc_samples):
        raise ValueError(
            "Number of samples" 
            f" ({len(wc_samples)})" 
            " must match number of trials"
            f" ({num_trials})."
        )
    return [
        Trial_Metadata(
            trial_num=trial, 
            num_events=num_events_per_trial, 
            num_subtrials=num_subtrials,
            split=split,
            lepton_flavor=lepton_flavor,
            wc_set=sample,
            wc_dist=wc_dist,
        ) for trial, sample in enumerate( 
            wc_samples
        )
    ]


def _make_subdir_name(
    metadata:Trial_Metadata,
) -> str:
    name = (
        f"{metadata.trial_num}"
        f"_{metadata.split}"
        f"_{metadata.num_events}"
        f"_{metadata.lepton_flavor}"
    )
    for wc in astuple(metadata.wc_set):
        name += f"_{wc:.2f}"
    return name


def _setup_subdirs(
    dir_:Path,
    metadatas:list[Trial_Metadata],
) -> None:
    if not dir_.is_dir():
        raise ValueError(
            "Data directory is not a directory."
        )
    dir_names = [
        _make_subdir_name(m) 
        for m in metadatas
    ]
    dir_paths = [
        dir_.joinpath(n) 
        for n in dir_names
    ]
    for dir_path, metadata in zip(
        dir_paths, 
        metadatas,
    ):
        dir_path.mkdir()
        metadata.to_json_file(
            dir_path.joinpath(metadata_file_name)
        )


def setup_dir(
    dir_:Path,  
    num_trials:int,
    wc_samples:list[WC_Set],
    num_events_per_trial:int,
    num_subtrials:int,
    split:str,
    lepton_flavor:str,
    wc_dist:Uniform_WC_Distribution,
) -> None:
    dir_.mkdir(exist_ok=True)
    metadatas = _make_metadatas(
        num_trials=num_trials,
        wc_samples=wc_samples, 
        num_events_per_trial=num_events_per_trial, 
        num_subtrials=num_subtrials, 
        split=split, 
        lepton_flavor=lepton_flavor, 
        wc_dist=wc_dist,
    )
    _setup_subdirs(
        dir_, 
        metadatas,
    )