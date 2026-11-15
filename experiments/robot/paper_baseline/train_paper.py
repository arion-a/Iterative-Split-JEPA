"""Run the SplitJEPA robot representation training (the paper's own code, unchanged) on our data. Run from the work directory:
    python train_paper.py TASK EPOCHS        # TASK = PickCube or PushCube
Only the SplitJEPA encoder is trained (the paper's single-latent LeJEPA baseline is not needed here)."""
import sys, os, time
os.chdir("robot"); sys.path.insert(0, ".")
from hl_maniskill.config import load_config
from hl_maniskill.train_splitjepa import train_splitjepa
task, epochs = sys.argv[1], sys.argv[2]
cfg = load_config([f"configs/{task.lower()}.yaml"], overrides=[f"rep.epochs={epochs}"], root=".")
t0 = time.time(); run = train_splitjepa(cfg, seed=0, tag=f"{task.lower()}_paper"); print("DONE", run, round(time.time() - t0), "s", flush=True)
