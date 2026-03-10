
from pathlib import Path
from subprocess import run
from dataclasses import dataclass
from functools import cached_property
from time import sleep

from .wc_types import WC_Set
from .util import append_to_path_stem, load_json
from .config import metadata_file_name, log_file_name, recon_file_name, sim_file_name, decay_file_name


def _write_dec_file(
    path: Path, 
    lepton_flavor: str, 
    wc_set: WC_Set, 
) -> None:

    if lepton_flavor not in ("e", "mu"):
        raise ValueError(
            f"Lepton flavor ({lepton_flavor})" 
            " must be 'e' or 'mu'."
        )
    
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
    1.000 MyK*0 {lepton_flavor}+ {lepton_flavor}- BTOSLLNPR 0 0 {wc_set.d_c_7} 0 1 {wc_set.d_c_9} 0 2 {wc_set.d_c_10} 0;
    Enddecay

    CDecay MyAntiB0

    Decay MyK*0
    1.000 K+ pi-   VSS;
    Enddecay

    CDecay MyAnti-K*0

    End
    """

    with open(path, "w") as file:
        file.write(content)


def _submit_job(
    lepton_flavor,
    num_events,
    sim_steer_file_path,
    recon_steer_file_path,
    decay_file_path,
    sim_file_path,
    recon_file_path,
    log_file_path,
):
    run(
        f'bsub -q l "basf2 {sim_steer_file_path} -- {decay_file_path} {sim_file_path} {num_events} &>> {log_file_path}'
        f' && basf2 {recon_steer_file_path} {lepton_flavor} {sim_file_path} {recon_file_path} &>> {log_file_path}'
        f' && rm {sim_file_path}"',
        shell=True,
    )


def _get_incomplete_dirs(
    dir_:Path
) -> list[Path]:
    
    def is_incomplete(dir_:Path):
        num_subtrials = load_json(
            dir_.joinpath(metadata_file_name)
        )["num_subtrials"]
        num_recon_files = len(list(
            dir_.glob(
                str(append_to_path_stem(
                    Path(recon_file_name), 
                    '*',
                )
            ))
        ))
        if num_subtrials != num_recon_files:
            return True
        return False
    
    return [
        p.parent
        for p in dir_.glob(metadata_file_name)
        if is_incomplete(p.parent)
    ]


@dataclass
class Job_Submitter:
    main_data_dir:Path
    recon_steer_file_path:Path
    sim_steer_file_path:Path
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
    
    def submit_jobs(
        self,
    ):
        for dir_ in _get_incomplete_dirs(self.main_data_dir):

            decay_file_path = dir_.joinpath(decay_file_name)
            log_file_path = dir_.joinpath(log_file_name)
            metadata_file_path = dir_.joinpath(metadata_file_name)

            metadata = load_json(metadata_file_path)

            _write_dec_file(
                decay_file_path, 
                metadata["lepton_flavor"], 
                metadata["wc_set"]
            )

            for subtrial in range(metadata["num_subtrials"]):

                sim_file_path = dir_.joinpath(
                    append_to_path_stem(Path(sim_file_name), f"_{subtrial}")
                )
                recon_file_path = dir_.joinpath(
                    append_to_path_stem(Path(recon_file_name), f"_{subtrial}")
                )

                _submit_job(
                    lepton_flavor=metadata["lepton_flavor"],
                    num_events=metadata["num_events..."], ######################################################3
                    sim_steer_file_path=self.sim_steer_file_path,
                    recon_steer_file_path=self.recon_steer_file_path,
                    decay_file_path=decay_file_path,
                    sim_file_path=sim_file_path,
                    recon_file_path=recon_file_path,
                    log_file_path=log_file_path,
                )

                self.num_submitted_jobs += 1

                if self.num_submitted_jobs % self.batch_size == 0:
                    sleep(self.batch_wait)
