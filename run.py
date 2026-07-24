from b2_run_sim import (
    Interval,
    RunMetadata,
    setup_run_dir,
    submit_jobs,
)

# Setup

debug = True

data_dir = "data/"
sim_steer_file_path = "steer_sim.py"
recon_steer_file_path = "steer_recon.py"
template_dec_file_path = "dec.dec"

vary_parameter_bounds = {
    "dC_7": Interval(0, 0),
    "dC_9": Interval(-2, 1),
    "dC_10": Interval(0, 0),
}
sm_parameter_bounds = {
    "dC_7": Interval(0, 0),
    "dC_9": Interval(0, 0),
    "dC_10": Interval(0, 0),
}


# Training dataset with varying parameters

train_vary_metadata = RunMetadata(
    split="train_vary",
    total_num_events=5_000_000,
    num_trials=1_000,  # each trial represents a different parameter configuration
    num_subtrials_per_trial=1,
    parameter_bounds=vary_parameter_bounds,
    sampling_type="grid",
    parameter_grid_counts={  # number of grid points along each axis
        "dC_7": 1,
        "dC_9": 1_000,
        "dC_10": 1,
    },
)

train_vary_dir = setup_run_dir(
    run_metadata=train_vary_metadata,
    parent_dir=data_dir,
)

submit_jobs(
    run_dir=train_vary_dir,
    sim_steer_file_path=sim_steer_file_path,
    recon_steer_file_path=recon_steer_file_path,
    template_dec_file_path=template_dec_file_path,
    debug=debug,
)


# Training dataset with Standard Model parameters

train_sm_metadata = RunMetadata(
    split="train_sm",
    total_num_events=5_000_000,
    num_trials=1,
    num_subtrials_per_trial=1_000,
    parameter_bounds=sm_parameter_bounds,
    sampling_type="grid",
    parameter_grid_counts={
        "dC_7": 1,
        "dC_9": 1,
        "dC_10": 1,
    },
)

train_sm_dir = setup_run_dir(
    run_metadata=train_sm_metadata,
    parent_dir=data_dir,
)

submit_jobs(
    run_dir=train_sm_dir,
    sim_steer_file_path=sim_steer_file_path,
    recon_steer_file_path=recon_steer_file_path,
    template_dec_file_path=template_dec_file_path,
    debug=debug,
)


# Validation dataset with randomly sampled parameters

val_metadata = RunMetadata(
    split="val",
    total_num_events=320_000,
    num_trials=20,
    num_subtrials_per_trial=1,
    parameter_bounds=vary_parameter_bounds,
    sampling_type="random",
)

val_dir = setup_run_dir(run_metadata=val_metadata, parent_dir=data_dir)

submit_jobs(
    run_dir=val_dir,
    sim_steer_file_path=sim_steer_file_path,
    recon_steer_file_path=recon_steer_file_path,
    template_dec_file_path=template_dec_file_path,
    debug=debug,
)
