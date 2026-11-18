"""Pod-side supervisor for E68 / E71 (docs/PLAN_NESTED_LOSS_STEPS.md). Resumable: re-running skips finished results.
    cd /workspace/n && PYTHONPATH=src python experiments/nested_sup.py            # reads P (max parallel jobs) from ./P each loop; status in ./status.json
Phase 1: one pilot per (experiment, strength, depth) with arm A (W for the world). Phase 2: a job queue, one job = one (exp, arm, strength, depth, seed); retried up to 3 times."""
import itertools, json, os, subprocess, sys, time
OUT = "results/nested"; os.makedirs("logs", exist_ok=True)
E68 = [("e68", arm, s, 4, seed) for arm in "AB" for s in (1, 2, 4, 8) for seed in range(250, 255)]
E71 = [("e71", arm, 0.5, K, seed) for arm in "AU" for K in (11, 13, 16) for seed in range(280, 285)]
order = [j for j in E71 if j[1] == "A"][::-1] + E68 + [j for j in E71 if j[1] == "U"]      # slowest first: K = 16, 13, 11 (A), then E68, then the untrained controls
def path(j):
    exp, arm, s, K, seed = j; folder = f"{OUT}/{exp}/{arm}/K{K}_s{s:g}" if exp == "e71" else f"{OUT}/{exp}/{arm}/s{s:g}"; return f"{folder}/main_seed{seed}.json"
def cmd(j, extra=()):
    exp, arm, s, K, seed = j; return ["python3", "-W", "ignore", "experiments/run_nested_loss.py", exp, "--arm", arm, "--strength", str(s), "--depth", str(K), "--seeds", str(seed), "--device", "cuda", *extra]
env = dict(os.environ, OMP_NUM_THREADS="1", MKL_NUM_THREADS="1", PYTHONPATH="src")
def status(**kw):
    done = sum(os.path.exists(path(j)) for j in order); json.dump({"done": done, "total": len(order), "time": time.time(), **kw}, open("status.json", "w"))
# phase 1: pilots (arm A, once per world)
worlds = sorted({(j[0], j[2], j[3]) for j in order if j[1] != "U"}, key=lambda w: -w[2])
pil = []
for exp, s, K in worlds:
    wp = f"{OUT}/{exp}/W_K{K}_s{s:g}.json"
    if not os.path.exists(wp):
        for stale in (wp + ".lock",):
            if os.path.exists(stale): os.remove(stale)
        pil.append((wp, subprocess.Popen(cmd((exp, "A", s, K, 0), ("--pilot-only",)), env=env, stdout=open(f"logs/pilot_{exp}_K{K}_s{s:g}.log", "w"), stderr=subprocess.STDOUT)))
status(phase="pilots", n_pilots=len(pil))
for wp, p in pil: p.wait()
# phase 2: queue
tries, running = {}, {}
while True:
    todo = [j for j in order if not os.path.exists(path(j)) and tries.get(j, 0) < 3 and j not in running]
    P = int(open("P").read()) if os.path.exists("P") else 40
    for j, p in list(running.items()):
        if p.poll() is not None:
            del running[j]
            if not os.path.exists(path(j)): tries[j] = tries.get(j, 0) + 1
    while todo and len(running) < P:
        j = todo.pop(0); tries.setdefault(j, 0)
        w = f"{OUT}/{j[0]}/W_K{j[3]}_s{j[2]:g}.json"
        if j[1] != "U" and os.path.exists(w) and json.load(open(w))["W"] is None: tries[j] = 99; continue     # no healthy W: world not run (a registered outcome)
        running[j] = subprocess.Popen(cmd(j), env=env, stdout=open(f"logs/{j[0]}_{j[1]}_K{j[3]}_s{j[2]:g}_{j[4]}.log", "a"), stderr=subprocess.STDOUT)
    status(phase="jobs", running=len(running), failed=[list(j) for j, t in tries.items() if t >= 3 and not os.path.exists(path(j))], P=P)
    if not running and not todo: break
    time.sleep(20)
status(phase="finished"); print("ALL DONE")
