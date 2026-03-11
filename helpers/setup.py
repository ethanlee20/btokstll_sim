
from dataclasses import astuple, asdict
from pathlib import Path
from random import seed, uniform

from .util import Uniform_WC_Dist, WC_Set, Metadata, Paths


class Sampler:
    def __init__(
        self, 
        dist:Uniform_WC_Dist,
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


def _make_metadata_list(
    num_trials,
    wc_samples:list[WC_Set],
    num_trial_events:int,
    num_subtrials:int,
    split:str,
    lepton_flavor:str,
    wc_dist:Uniform_WC_Dist,
) -> list[Metadata]:
    if num_trials != len(wc_samples):
        raise ValueError(
            "Number of samples" 
            f" ({len(wc_samples)})" 
            " must match number of trials"
            f" ({num_trials})."
        )
    return [
        Metadata(
            trial, 
            num_trial_events, 
            num_subtrials,
            split,
            lepton_flavor,
            sample,
            wc_dist,
        ) for trial, sample in enumerate( 
            wc_samples
        )
    ]


def _make_subdir_name(
    metadata:Metadata,
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
    metadata_list:list[Metadata],
) -> None:
    if not dir_.is_dir():
        raise ValueError(
            "Data directory is not a directory."
            f" ({dir_})"
        )
    dir_paths = [
        dir_.joinpath(_make_subdir_name(m)) 
        for m in metadata_list
    ]
    for p, m in zip(
        dir_paths, 
        metadata_list,
    ):
        p.mkdir()
        m.to_json_file(
            Paths(p).metadata_file_name
        )


def setup_dir(
    dir_:Path,  
    num_trials:int,
    wc_samples:list[WC_Set],
    num_trial_events:int,
    num_subtrials:int,
    split:str,
    lepton_flavor:str,
    wc_dist:Uniform_WC_Dist,
) -> None:
    dir_.mkdir(exist_ok=True)
    _setup_subdirs(
        dir_,
        _make_metadata_list(
            num_trials,
            wc_samples, 
            num_trial_events, 
            num_subtrials, 
            split, 
            lepton_flavor, 
            wc_dist,
        )
    )