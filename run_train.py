from b2_run_sim import (
    Interval,
    RunMetadata,
    setup_run_dir,
    submit_jobs,
)

# Setup

debug = False

data_dir = "data/"
sim_steer_file_path = "steer_sim.py"
recon_steer_file_path = "steer_recon.py"
template_dec_file_path = "dec.dec"

parameter_bounds = {
    "dC_7": Interval(-0.1, 0.1),
    "dC_9": Interval(-2, 1),
    "dC_10": Interval(0, 0),
}


# Metadata

metadatas = [
    RunMetadata(
        split="train",
        total_num_events=18_000_000,
        num_trials=900,
        num_subtrials_per_trial=1,
        parameter_bounds=parameter_bounds,
        sampling_type="grid",
        parameter_grid_counts={
            "dC_7": 30,
            "dC_9": 30,
            "dC_10": 1,
        },
    ),
    RunMetadata(
        split="val",
        total_num_events=2_880_000,
        num_trials=100,
        num_subtrials_per_trial=1,
        parameter_bounds=parameter_bounds,
        sampling_type="grid",
        parameter_grid_counts={
            "dC_7": 10,
            "dC_9": 10,
            "dC_10": 1,
        }
    ),
    RunMetadata(
        split="val_sets",
        total_num_events=1_600_000,
        num_trials=100,
        num_subtrials_per_trial=1,
        parameter_bounds=parameter_bounds,
        sampling_type="random",
    ),
]


# Setup directories

dirs = [setup_run_dir(metadata, data_dir) for metadata in metadatas]


# Submit jobs

for dir_ in dirs:
    submit_jobs(
        run_dir=dir_,
        sim_steer_file_path=sim_steer_file_path,
        recon_steer_file_path=recon_steer_file_path,
        template_dec_file_path=template_dec_file_path,
        debug=debug,
    )
