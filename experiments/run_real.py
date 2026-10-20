"""Stage V P5: the same discovery pipeline on real double-pendulum video. Informational only (10 clips, held out in time, partial tracker proxies)."""
from __future__ import annotations

import argparse
import hashlib
import json
import os

import numpy as np
import torch
import yaml
from scipy.stats import spearmanr

from isj import explog, quotient_audit as qa, real_video, real_video_io as rio, temporal_ladder as tl
from isj.pipeline import Pipeline


def main(cfg, out, log):
    rng = np.random.default_rng(cfg["seed"])
    paths = [f"data/real/morpheus/v{i}.mp4" for i in cfg["videos"]]
    gray = [rio.decode(p, tuple(cfg["crop"]), cfg["size"]) for p in paths]
    rgb = [rio.decode(p, tuple(cfg["crop"]), 128, fmt="rgb") for p in paths]
    t = min(len(g) for g in gray)
    frames = np.stack([rio.illumination_views(g[:t], rng, cfg["nuisance_amp"], cfg["size"]) for g in gray])       # (R, 2, T, D)
    track = [real_video.orange_track(r[:t]) for r in rgb]
    prox = [real_video.proxies(tr, cfg["fps"]) for tr in track]
    t0, t1 = int(cfg["time_split"][0] * t), int(cfg["time_split"][1] * t)
    sl = {"train": slice(0, t0), "val": slice(t0, t1), "test": slice(t1, t)}
    pipe = Pipeline(frames[:, :, sl["train"]], cfg, cfg["seed"])
    zw = {k: pipe.whiten(pipe.latent(frames[:, :, s])) for k, s in sl.items()}
    ladder = tl.run_ladder(zw["train"], cfg["lags"], cfg["gamma_min"], 0.99, False, cfg["seed"], cfg["s1_chance_fraction"])
    psi = tl.fit_psi(zw["train"], ladder["core"])
    q = {k: tl.apply_psi(v, psi) for k, v in zw.items()}
    cert = qa.certificate(q["train"], q["val"], q["test"], cfg["horizon_K"], cfg["delta_std"], cfg["n_pairs"], cfg["seed"])
    res = {"n_videos": len(paths), "frames_per_video": t, "fps": cfg["fps"], "stop": ladder["stop"], "core_dim": int(ladder["core"].shape[1]),
           "ladder": [{k: v for k, v in x.items() if k not in ("V", "Q")} for x in ladder["rungs"]], "psi_icc_fit": psi["icc_fit"], "certificate": cert,
           "tracker_detect_fraction": float(np.mean([np.isfinite(tr).all() for tr in track])), "informational": {}}
    for name in ("speed2", "height"):
        y = {k: np.repeat(np.stack([p[name][1 + s.start: (s.stop if s.stop else t)] for p in prox])[:, None, :], 2, 1)[..., None] for k, s in sl.items()}
        y["test"] = y["test"][:, :, : q["test"].shape[2]]
        a = np.concatenate([zw["train"].reshape(-1, zw["train"].shape[-1]), np.ones((zw["train"].size // zw["train"].shape[-1], 1))], 1)
        yt = np.repeat(np.stack([p[name][1 + sl["train"].start: sl["train"].stop] for p in prox])[:, None, :], 2, 1).reshape(-1, 1)
        w, *_ = np.linalg.lstsq(a, yt, rcond=None)
        xt = zw["test"].reshape(-1, zw["test"].shape[-1]); yte = y["test"].reshape(-1, 1)
        pred = np.concatenate([xt, np.ones((len(xt), 1))], 1) @ w
        res["informational"][name] = {"abs_spearman_psi_test": abs(float(spearmanr(q["test"].ravel(), y["test"].ravel())[0])),
                                      "ceiling_probe_r2_test_report_only": float(1 - ((yte - pred) ** 2).sum() / ((yte - yte.mean()) ** 2).sum())}
    os.makedirs(out, exist_ok=True)
    path = os.path.join(out, "morpheus.json")
    with open(path, "x") as f:
        json.dump(res, f, indent=1)
    print(json.dumps({k: v for k, v in res.items() if k != "ladder"}, indent=1))
    log("run", "Real double-pendulum video (10 public clips) through the discovery pipeline", {"stop": res["stop"], "core_dim": res["core_dim"], "certificate": {k: round(v, 4) for k, v in cert.items()}, "informational": res["informational"]}, [path])


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--config", default="configs/real.yaml"); ap.add_argument("--out", default="results/real"); ap.add_argument("--no-log", action="store_true")
    a = ap.parse_args(); cfg = yaml.safe_load(open(a.config))
    torch.set_num_threads(2)
    main(cfg, a.out, (lambda *x, **k: None) if a.no_log else (lambda kind, what, outputs, arts: explog.append(kind, what, stage="V", step="P5", how="experiments/run_real.py", outputs=outputs, artifact_paths=arts)))
