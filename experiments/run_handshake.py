"""Stage V P2-P3: pilot + handshake. Three seeds, arms main / flat / shuffled, evaluator-side naming and references.

    python experiments/run_handshake.py --out results/handshake [--seeds 0 1 2] [--no-log]
Refuses to run if the criteria differ from configs/handshake.criteria.sha256. Results are never overwritten.
"""
from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import os
import sys
import time

import numpy as np
import torch
import yaml
from scipy.stats import spearmanr

from isj import explog, handshake_eval as ev, quotient_audit as qa, temporal_ladder as tl, video_encoder as ve
from isj.pipeline import Pipeline
from isj.video_io import load_frames


def criteria_hash(cfg):
    return hashlib.sha256(json.dumps(cfg["criteria"], sort_keys=True).encode()).hexdigest()


def run(cfg, seeds, out, log, data_root="data/handshake"):
    crit = cfg["criteria"]; lad = crit["ladder"]; cert = crit["certificate"]
    data = {s: load_frames(f"{data_root}/seed{s}") for s in seeds}
    evals = {s: ev.aligned(f"{data_root}/seed{s}") for s in seeds}
    pipes, arms_psi, res = {}, {}, {}
    for s in seeds:
        t0 = time.time()
        frames, split = data[s]
        pipe = Pipeline(frames[split == 0], cfg, s)
        z = pipe.latent(frames); zw = pipe.whiten(z)
        print(f"seed {s}: encoder trained {time.time() - t0:.0f}s, min std {pipe.log[-1]['min_std']:.2f}", flush=True)
        main = tl.run_ladder(zw[split == 0], lad["lags"], lad["gamma_min"], lad["b2_quantile"], False, s, s1_chance_fraction=lad["s1_chance_fraction"])
        shuf = tl.run_ladder(zw[split == 0], lad["lags"], lad["gamma_min"], lad["b2_quantile"], True, s, s1_chance_fraction=lad["s1_chance_fraction"])
        psi_main = tl.fit_psi(zw[split == 0], main["core"]); psi_shuf = tl.fit_psi(zw[split == 0], shuf["core"])
        q = {"main": tl.apply_psi(zw, psi_main), "shuffled": tl.apply_psi(zw, psi_shuf)}
        zc = z - pipe.zmean
        qf = (zc @ pipe.flat_dir)[..., None]
        q["flat"] = (qf - qf[split == 0].mean()) / qf[split == 0].std()
        pipes[s] = (pipe, main, psi_main)
        r = {"seed": s, "encoder_log": pipe.log, "ladder_main": [{k: v for k, v in x.items() if k not in ("V", "Q")} for x in main["rungs"]],
             "stop_main": main["stop"], "core_dim_main": int(main["core"].shape[1]),
             "ladder_shuffled_stop": shuf["stop"], "core_dim_shuffled": int(shuf["core"].shape[1]), "arms": {}}
        for arm, qa_ in q.items():
            c = qa.certificate(qa_[split == 0], qa_[split == 1], qa_[split == 2], cert["horizon_K"], cert["delta_std"], cert["n_pairs"], s)
            c["naming_abs_spearman"] = ev.naming(qa_[split == 2], evals[s]["E"][split == 2])
            r["arms"][arm] = c
        r["references"] = ev.references(evals[s], split, cert["horizon_K"], cert["delta_std"], cert["n_pairs"], s)
        r["ceiling_probe_report_only"] = ev.ceiling_probe(zw, evals[s]["E"], split)
        v2 = next((x["V"] for x in main["rungs"] if x["family"] == f"lag{lad['lags'][0]}" and "V" in x), None)
        if v2 is not None:
            r["reach_variant_block"] = ev.reach_curve(zw @ v2, split)
        r["reach_psi"] = ev.reach_curve(q["main"], split)
        res[s] = r
        arms_psi[s] = q
    # P-stab: each seed's psi function applied to the common frames (seed-0 test releases), compared across seeds
    f0, sp0 = data[seeds[0]]
    common = f0[sp0 == 2]
    cq = {}
    for s in seeds:
        pipe, main, psi = pipes[s]
        cq[s] = tl.apply_psi(pipe.whiten(pipe.latent(common)), psi).ravel()
    stab = {f"{a}-{b}": abs(float(spearmanr(cq[a], cq[b])[0])) for a, b in itertools.combinations(seeds, 2)}
    for s in seeds:
        res[s]["pilot_stability_pairs"] = stab
        path = os.path.join(out, "main", f"{s}.json")
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "x") as f:
            json.dump(res[s], f, indent=1)
        log("run", f"Handshake seed {s} finished", s, {"stop": res[s]["stop_main"], "core_dim": res[s]["core_dim_main"], "arms": {a: {k: round(v, 4) for k, v in c.items() if k in ('V','icc','L','rollout_nmse','naming_abs_spearman')} for a, c in res[s]["arms"].items()}}, [path])
    return res, stab


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default="configs/handshake.yaml"); ap.add_argument("--out", default="results/handshake")
    ap.add_argument("--seeds", type=int, nargs="*"); ap.add_argument("--no-log", action="store_true"); ap.add_argument("--data-root", default="data/handshake")
    a = ap.parse_args()
    cfg = yaml.safe_load(open(a.config))
    if criteria_hash(cfg) != open(a.config.replace(".yaml", ".criteria.sha256")).read().strip():
        sys.exit("criteria differ from the frozen hash")
    seeds = a.seeds if a.seeds else cfg["seeds"]
    def log(kind, what, seed, outputs, arts):
        if not a.no_log:
            explog.append(kind, what, stage="V", step="P2/P3", how="experiments/run_handshake.py", outputs=outputs, artifact_paths=arts)
    torch.set_num_threads(4)
    run(cfg, seeds, a.out, log, a.data_root)
