"""Paper figures for stage V (LIVE_DATA_PLAN §6), minimal: FIG 1 psi over two test releases beside their energy, FIG 2 psi against energy
(all held-out frames, seed 0) with the verdict table, FIG 3 reach curves. Writes results/figures/*.svg and results/figures/fig_data.json.
FIG 1-2 retrain the seed-0 handshake pipeline (same recipe and seed as the registered run, about 3 min CPU)."""
from __future__ import annotations

import glob
import json
import os

import numpy as np
import torch
import yaml

from isj import handshake_eval as ev, temporal_ladder as tl
from isj.pipeline import Pipeline
from isj.video_io import load_frames

W, H, M = 560, 360, 50
C = {"a": "#2a78d6", "b": "#eb6834", "ink": "#0b0b0b", "mut": "#898781", "grid": "#e1e0d9"}


def frame(title, xlabel, ylabel, body, w=W, h=H):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}"><rect width="100%" height="100%" fill="#fcfcfb"/>'
            f'<text x="{M}" y="22" font="600 14px sans-serif" font-family="sans-serif" font-size="14" fill="{C["ink"]}">{title}</text>'
            f'<line x1="{M}" y1="{h - M}" x2="{w - 20}" y2="{h - M}" stroke="{C["mut"]}"/><line x1="{M}" y1="35" x2="{M}" y2="{h - M}" stroke="{C["mut"]}"/>'
            f'<text x="{w / 2}" y="{h - 12}" font-family="sans-serif" font-size="12" text-anchor="middle" fill="{C["mut"]}">{xlabel}</text>'
            f'<text x="14" y="{h / 2}" font-family="sans-serif" font-size="12" text-anchor="middle" fill="{C["mut"]}" transform="rotate(-90 14 {h / 2})">{ylabel}</text>{body}</svg>')


def scale(v, lo, hi, a, b):
    return a + (np.asarray(v) - lo) / (hi - lo + 1e-12) * (b - a)


def polyline(x, y, xr, yr, col, w=W, h=H, dash=""):
    px, py = scale(x, *xr, M, w - 20), scale(y, *yr, h - M, 40)
    pts = " ".join(f"{a:.1f},{b:.1f}" for a, b in zip(px, py))
    return f'<polyline fill="none" stroke="{col}" stroke-width="1.6" points="{pts}" {dash}/>'


def main():
    cfg = yaml.safe_load(open("configs/handshake.yaml")); lad = cfg["criteria"]["ladder"]
    os.makedirs("results/figures", exist_ok=True)
    torch.set_num_threads(4)
    frames, split = load_frames("data/handshake/seed0")
    e_all = ev.aligned("data/handshake/seed0")["E"]
    pipe = Pipeline(frames[split == 0], cfg, 0)
    zw = pipe.whiten(pipe.latent(frames))
    out = tl.run_ladder(zw[split == 0], lad["lags"], lad["gamma_min"], lad["b2_quantile"], False, 0, s1_chance_fraction=lad["s1_chance_fraction"])
    q = tl.apply_psi(zw, tl.fit_psi(zw[split == 0], out["core"]))[..., 0]          # (R, A, T)
    te = np.flatnonzero(split == 2)
    e_te, q_te = e_all[te, 0, :, 0], q[te, 0]
    sign = np.sign(np.corrcoef(q_te.ravel(), e_te.ravel())[0, 1])                 # direction sign is arbitrary
    q_te = sign * q_te
    ez = (e_te - e_te.mean()) / e_te.std()
    order = np.argsort(e_te.mean(1))
    lo_r, hi_r = order[len(order) // 6], order[-1]                                  # a low-energy and the highest-energy test release
    t = np.arange(q_te.shape[1])
    body = polyline(t, q_te[lo_r], (0, t[-1]), (-3, 3), C["a"]) + polyline(t, ez[lo_r] * np.ones_like(t), (0, t[-1]), (-3, 3), C["b"], dash='stroke-dasharray="5 3"')
    body += polyline(t, q_te[hi_r], (0, t[-1]), (-3, 3), C["a"]) + polyline(t, ez[hi_r] * np.ones_like(t), (0, t[-1]), (-3, 3), C["b"], dash='stroke-dasharray="5 3"')
    open("results/figures/fig1_psi_vs_energy_time.svg", "w").write(frame("FIG 1  psi (solid) and energy (dashed), two held-out releases, standardized", "frame", "standardized value", body))
    dots = "".join(f'<circle cx="{scale(a, -2.5, 2.5, M, W - 20):.1f}" cy="{scale(b, -3, 3, H - M, 40):.1f}" r="1.6" fill="{C["a"]}" fill-opacity="0.35"/>' for a, b in zip(ez.ravel()[::7], q_te.ravel()[::7]))
    rho = ev.naming(q_te, e_te)
    open("results/figures/fig2_psi_vs_energy_scatter.svg", "w").write(frame(f"FIG 2  psi against energy, held-out frames (seed 0), |Spearman| {rho:.3f}", "energy (standardized)", "psi (standardized)", dots))
    runs = [json.load(open(p)) for p in sorted(glob.glob("results/handshake/main/*.json"))]
    hs = [1, 2, 4, 8, 16, 32]
    pm = [np.mean([r["reach_psi"][str(h)] for r in runs]) for h in hs]
    vm = [np.mean([r["reach_variant_block"][str(h)] for r in runs if "reach_variant_block" in r]) for h in hs]
    body = polyline(np.log2(hs), pm, (0, 5), (0, 1), C["a"]) + polyline(np.log2(hs), vm, (0, 5), (0, 1), C["b"])
    open("results/figures/fig3_reach.svg", "w").write(frame("FIG 3  reach: held-out error vs horizon (blue: psi, orange: fast block)", "log2 horizon (frames)", "normalized MSE", body))
    json.dump({"fig2_abs_spearman_seed0": rho, "fig3_psi": pm, "fig3_variant": vm, "horizons": hs, "fig1_releases": [int(te[lo_r]), int(te[hi_r])]}, open("results/figures/fig_data.json", "w"), indent=1)
    print("figures written", rho)


if __name__ == "__main__":
    main()
