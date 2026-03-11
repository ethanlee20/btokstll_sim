
from pathlib import Path

from helpers import Sampler, Uniform_WC_Dist, Interval, setup_dir, submit_jobs


run_setup = False
run_submit = True

sim_steer_file_path = Path("steering/steer_sim.py")
recon_steer_file_path = Path("steering/steer_recon.py")



data_dir = Path("data/vary_one/vary_7_train")

num_trials = 10
dist = Uniform_WC_Dist(
    d_c_7=Interval(-0.5, 0.5), 
    d_c_9=Interval(0, 0), 
    d_c_10=Interval(0, 0),
)

if run_setup:
    samples = (
        Sampler(dist)
        .sample(num_trials)
    )
    setup_dir(
        data_dir, 
        num_trials=num_trials, 
        wc_samples=samples, 
        num_trial_events=20, 
        num_subtrials=2, 
        split="train", 
        lepton_flavor="mu", 
        wc_dist=dist,
    )
if run_submit:
    submit_jobs(
        data_dir, 
        sim_steer_file_path, 
        recon_steer_file_path, 
        debug=True
    )