
"""
Generate Standard Model events!
"""

from pathlib import Path

from helpers import Sampler, Uniform_WC_Dist, Interval, setup_dir, submit_jobs


run_setup = True
run_submit = True
debug = True

sim_steer_file_path = Path("steering/steer_sim.py")
recon_steer_file_path = Path("steering/steer_recon.py")
data_dir = Path("data/sm")

dist = Uniform_WC_Dist(
    d_c_7=Interval(0, 0), 
    d_c_9=Interval(0, 0), 
    d_c_10=Interval(0, 0),
)

num_trials = 30
num_trial_events = 10_000
num_subtrials = 1
split = "_"
lepton_flavor = "mu"


if run_setup:
    samples = (
        Sampler(dist)
        .sample(num_trials)
    )
    setup_dir(
        data_dir, 
        samples, 
        num_trial_events, 
        num_subtrials, 
        split, 
        lepton_flavor, 
        dist,
    )
if run_submit:
    submit_jobs(
        data_dir, 
        sim_steer_file_path, 
        recon_steer_file_path, 
        debug=debug
    )