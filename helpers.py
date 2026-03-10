

from dataclasses import dataclass, astuple, asdict
from random import seed, uniform
from functools import cached_property
from json import dump, load


def safer_convert_to_int(
    x,
):
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


@dataclass(frozen=True)
class Uniform_WC_Distribution:
    d_c_7: Interval 
    d_c_9: Interval 
    d_c_10: Interval 


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
    ):
        with open(path, 'x') as file:
            dump(
                asdict(self), 
                file, 
                indent=4,
            )

    @classmethod
    def from_json_file(
        cls, 
        path,
    ):
        # Requires manual object reconstruction.

        with open(path, 'r') as file:
            metadata_dict = load(file)
        
        def reconstruct(dict, key, cls_):
            dict[key] = cls_(**dict[key])
        
        reconstruct(
            metadata_dict, 
            "delta_wilson_coefficient_set", 
            Delta_Wilson_Coefficient_Set
        )
        for key in metadata_dict["delta_wilson_coefficient_distribution"].keys():
            reconstruct(
                metadata_dict["delta_wilson_coefficient_distribution"],
                key, 
                Interval
            )
        reconstruct(
            metadata_dict,
            "delta_wilson_coefficient_distribution", 
            Uniform_Delta_Wilson_Coefficient_Distribution
        )
        return cls(**metadata_dict)
    

@dataclasses.dataclass(frozen=True)
class Directory_Manager:
    main_data_dir: Path
    num_trials: int
    num_subtrials: int
    num_events_per_trial: int
    split: str
    lepton_flavor: str
    delta_wilson_coefficient_set_samples: list[Delta_Wilson_Coefficient_Set]
    delta_wilson_coefficient_distribution: Uniform_Delta_Wilson_Coefficient_Distribution
    metadata_file_name: str = "metadata.json"

    def __post_init__(
        self
    ):
        if not self.main_data_dir.is_dir():
            raise ValueError(
                "Main data directory not found"
                f" ({self.main_data_dir})."
            )
        if self.num_trials != len(self.delta_wilson_coefficient_set_samples):
            raise ValueError(
                "Number of samples" 
                f" ({len(self.delta_wilson_coefficient_set_samples)})" 
                " must match number of trials"
                f" ({self.num_trials})."
            )
        
    @functools.cached_property
    def trial_range(
        self
    ):
        start = self._largest_existing_trial_num + 1 
        end = start + self.num_trials
        return range(start, end)
    
    @functools.cached_property
    def metadata_list(
        self
    ):
        return [
            Trial_Metadata(
                trial_num=trial, 
                num_events=self.num_events_per_trial, 
                num_subtrials=self.num_subtrials,
                split=self.split,
                lepton_flavor=self.lepton_flavor,
                wc_set=sample,
                wc_dist=self.delta_wilson_coefficient_distribution,
            ) for trial, sample in zip(
                self.trial_range, 
                self.delta_wilson_coefficient_set_samples
            )
        ]

    @functools.cached_property
    def _largest_existing_trial_num(
        self
    ):
        paths_files_metadata = self.main_data_dir.rglob(
            self.metadata_file_name
        )
        metadatas = [
            Trial_Metadata.from_json_file(p) 
            for p in paths_files_metadata
        ]
        trial_nums = [m.trial_num for m in metadatas]
        largest = -1 if trial_nums == [] else max(trial_nums)
        return largest
    
    def setup_dirs(
        self
    ):
        def dir_name(m:Trial_Metadata):
            name = (
                f"{m.trial_num}"
                f"_{m.split}"
                f"_{m.num_events}"
                f"_{m.lepton_flavor}"
            )
            for c in dataclasses.astuple(
                m.wc_set
            ):
                name += f"_{c:.2f}"
            return name

        dir_names = [dir_name(m) for m in self.metadata_list]
        dir_paths = [self.main_data_dir.joinpath(n) for n in dir_names]
        for dir_, metadata in zip(dir_paths, self.metadata_list):
            dir_.mkdir()
            metadata.to_json_file(dir_.joinpath(self.metadata_file_name))


def write_dec_file(
    file_path: Path, 
    lepton_flavor: str, 
    delta_wilson_coefficient_set: Delta_Wilson_Coefficient_Set, 
):

    if lepton_flavor not in ("e", "mu"):
        raise ValueError(
            f"Lepton flavor ({lepton_flavor}) must be 'e' or 'mu'."
        )
    
    delta_c_7 = delta_wilson_coefficient_set.delta_c_7
    delta_c_9 = delta_wilson_coefficient_set.delta_c_9
    delta_c_10 = delta_wilson_coefficient_set.delta_c_10

    content = f"""
    Alias MyB0 B0
    Alias MyAntiB0 anti-B0
    ChargeConj MyB0 MyAntiB0

    Alias MyK*0 K*0
    Alias MyAnti-K*0 anti-K*0
    ChargeConj MyK*0 MyAnti-K*0

    Decay Upsilon(4S)
    0.500  MyB0 anti-B0    VSS;
    0.500  B0 MyAntiB0    VSS;
    Enddecay

    Decay MyB0
    1.000 MyK*0 {lepton_flavor}+ {lepton_flavor}- BTOSLLNPR 0 0 {delta_c_7} 0 1 {delta_c_9} 0 2 {delta_c_10} 0;
    Enddecay

    CDecay MyAntiB0

    Decay MyK*0
    1.000 K+ pi-   VSS;
    Enddecay

    CDecay MyAnti-K*0

    End
    """

    with open(file_path, "w") as f:
        f.write(content)


def submit_job(
    lepton_flavor,
    num_events,
    sim_steer_file_path,
    recon_steer_file_path,
    decay_file_path,
    sim_file_path,
    recon_file_path,
    log_file_path,
):
    subprocess.run(
        f'bsub -q l "basf2 {sim_steer_file_path} -- {decay_file_path} {sim_file_path} {num_events} &>> {log_file_path}'
        f' && basf2 {recon_steer_file_path} {lepton_flavor} {sim_file_path} {recon_file_path} &>> {log_file_path}'
        f' && rm {sim_file_path}"',
        shell=True,
    )


@dataclasses.dataclass
class Job_Submitter:
    main_data_dir:Path
    recon_steer_file_path:Path
    sim_steer_file_path:Path
    metadata_file_name:Path = Path("metadata.json")
    recon_file_name:Path = Path("recon.root")
    sim_file_name:Path = Path("sim.root")
    decay_file_name:Path = Path("decay.dec")
    log_file_name:Path = Path("log.log")
    batch_size:int = 500
    batch_wait:int = 300

    def __post_init__(
        self,
    ):
        if not self.main_data_dir.is_dir():
            raise ValueError(
                "Main data directory not found"
                f" ({self.main_data_dir})."
            )
        
        self.num_submitted_jobs = 0
    
    @property
    def incomplete_dirs(
        self
    ):
        def is_incomplete(dir_:Path):
            num_subtrials = Trial_Metadata.from_json_file(
                dir_.joinpath(self.metadata_file_name)
            ).num_subtrials
            num_recon_files = len(list(
                dir_.glob(str(
                    append_to_stem(self.recon_file_name, '*')
                ))
            ))
            if num_subtrials != num_recon_files:
                return True
            return False
        
        return [
            p for p in self._all_candidate_dirs 
            if is_incomplete(p)
        ] 
    
    @functools.cached_property
    def _all_candidate_dirs(
        self
    ):
        metadata_file_paths = self.main_data_dir.rglob(str(
            self.metadata_file_name
        ))
        return [p.parent for p in metadata_file_paths]

    def submit_jobs(
        self,
    ):
        for dir_ in self.incomplete_dirs:

            decay_file_path = dir_.joinpath(self.decay_file_name)
            log_file_path = dir_.joinpath(self.log_file_name)
            metadata_file_path = dir_.joinpath(self.metadata_file_name)

            metadata = Trial_Metadata.from_json_file(metadata_file_path)

            write_dec_file(
                decay_file_path, 
                metadata.lepton_flavor, 
                metadata.wc_set
            )

            for subtrial in range(metadata.num_subtrials):

                sim_file_path = dir_.joinpath(
                    append_to_stem(self.sim_file_name, subtrial)
                )
                recon_file_path = dir_.joinpath(
                    append_to_stem(self.recon_file_name, subtrial)
                )

                submit_job(
                    lepton_flavor=metadata.lepton_flavor,
                    num_events=metadata.num_events_per_subtrial,
                    sim_steer_file_path=self.sim_steer_file_path,
                    recon_steer_file_path=self.recon_steer_file_path,
                    decay_file_path=decay_file_path,
                    sim_file_path=sim_file_path,
                    recon_file_path=recon_file_path,
                    log_file_path=log_file_path,
                )

                self.num_submitted_jobs += 1

                if self.num_submitted_jobs % self.batch_size == 0:
                    time.sleep(self.batch_wait)
