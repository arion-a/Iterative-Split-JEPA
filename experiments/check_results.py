"""Minimal integrity checks for the completion plan (docs/COMPLETION_PLAN.md).

usage: python experiments/check_results.py {e21b1,e21b2,e23,data,feat,evidence} [--final]
Without --final, only files that exist are checked (progress check); with --final the expected count must be complete.
Exit code 1 on any failure. Checks are about integrity (right files, right seeds, finite numbers, right shapes),
not about whether a claim holds; the claims are scored by the analysis scripts against the registered text.
"""
import glob, json, math, os, subprocess, sys
import numpy as np

BASE = "b0c0a10"  # commit before any E21-E24 outcome line was written; EVIDENCE.md may only gain lines after it


def finite(o):
    if isinstance(o, float): return math.isfinite(o)
    if isinstance(o, dict): return all(finite(v) for v in o.values())
    if isinstance(o, (list, tuple)): return all(finite(v) for v in o)
    return True


def report(name, bad, n, want, final):
    miss = f", {want - n} missing" if n < want else ""
    ok = not bad and (n >= want or not final)
    print(f"{'PASS' if ok else 'FAIL'} {name}: {n}/{want} files{miss}" + (f"; problems: {bad[:5]}" if bad else ""))
    return ok


def check_b1(folder, seeds, arms, final):
    bad, n = [], 0
    for a in arms:
        for s in seeds:
            p = f"{folder}/{a}_seed{s}.json"
            if not os.path.exists(p): continue
            n += 1
            d = json.load(open(p))
            if d.get("seed") != s: bad.append(f"{p}: seed {d.get('seed')}")
            if not finite(d): bad.append(f"{p}: non-finite number")
            if not d.get("rungs"): bad.append(f"{p}: no rungs")
    return report(folder, bad, n, len(seeds) * len(arms), final)


def check_b2(folder, seeds, sigmas, final):
    bad, n = [], 0
    for sg in sigmas:
        for s in seeds:
            p = f"{folder}/sigma_cat_{sg}/{s}.json"
            if not os.path.exists(p): continue
            n += 1
            d = json.load(open(p))
            if d.get("seed") != s or abs(d.get("sigma_cat", -1) - sg) > 1e-9: bad.append(f"{p}: seed/sigma mismatch")
            if not finite(d): bad.append(f"{p}: non-finite number")
            if not d.get("image_geometry"): bad.append(f"{p}: image_geometry (E22 field) missing")
            if "purify" not in d or "noop_control" not in d: bad.append(f"{p}: purify/noop fields missing")
    return report(folder, bad, n, len(seeds) * len(sigmas), final)


def check_data(final):
    ok = True
    for t in ("PickCube", "PushCube"):
        bad, fs = [], sorted(glob.glob(f"data/robot/{t}/group_*.npz"))
        for f in fs:
            z = np.load(f)
            im = z["images"]
            if im.shape != (8, 30, 2, 128, 128, 3) or im.dtype != np.uint8: bad.append(f"{f}: images {im.shape}")
            elif im.std() < 5 or np.abs(im[:, :, 0].astype(int) - im[:, :, 1].astype(int)).mean() < 1: bad.append(f"{f}: blank or identical cameras")
            if not np.isfinite(z["state"]).all(): bad.append(f"{f}: state not finite")
            if not z["success"].all(): bad.append(f"{f}: unsuccessful trajectory")
        ok &= report(f"data/{t}", bad, len(fs), 100, final)
    return ok


def check_feat(final):
    ok = True
    for t in ("PickCube", "PushCube"):
        bad, fs = [], sorted(glob.glob(f"data/robot/feat/{t}/group_*.npy"))
        for f in fs:
            a = np.load(f)
            if a.shape != (8, 30, 2, 2048) or not np.isfinite(a.astype(np.float32)).all(): bad.append(f"{f}: {a.shape}")
        ok &= report(f"feat/{t}", bad, len(fs), 100, final)
    return ok


def check_enc(final):
    ok, spec = True, [("results/stage_b1_e25", ["main"], 5), ("results/stage_b1_e26", ["main", "shuffled_rung2"], 10),
                      ("results/stage_b1_e27/mirror_lejepa", ["main"], 5), ("results/stage_b1_e27/mlp_lejepa", ["main"], 5), ("results/stage_b1_e27/mirror_predict", ["main"], 5)]
    for folder, arms, want in spec:
        bad, n = [], 0
        for a in arms:
            for s in range(30, 35):
                p = f"{folder}/{a}_seed{s}.json"
                if not os.path.exists(p): continue
                n += 1
                d = json.load(open(p))
                pr = d.get("presence", {})
                if d.get("seed") != s or not finite(d): bad.append(f"{p}: seed/finite")
                if any(len(pr.get(k, [])) != 3 or not all(-1 <= x <= 1.01 for x in pr.get(k, [])) for k in ("linear", "mlp")): bad.append(f"{p}: presence field")
                if d["encoder_final"]["min_std"] < 0.1: bad.append(f"{p}: encoder collapsed (min std {d['encoder_final']['min_std']:.3f})")
        ok &= report(folder, bad, n, want, final)
    return ok


def check_evidence():
    out = subprocess.run(["git", "diff", "--numstat", BASE, "--", "docs/EVIDENCE.md"], capture_output=True, text=True).stdout.split()
    dele = int(out[1]) if len(out) >= 2 else 0
    print(f"{'PASS' if dele == 0 else 'FAIL'} EVIDENCE.md: {dele} lines deleted or changed since {BASE} (must be 0: predictions are never edited)")
    return dele == 0


if __name__ == "__main__":
    mode, final = sys.argv[1], "--final" in sys.argv
    seeds = list(range(20, 30))
    ok = {"e21b1": lambda: check_b1("results/stage_b1_e21", seeds, ["main", "shuffled_rung2", "rank1_rung2"], final),
          "e21b2": lambda: check_b2("results/stage_b2_e21", seeds, [0.1, 0.4], final),
          "e23": lambda: check_b1("results/stage_b1_e23", list(range(30, 35)), ["main", "shuffled_rung2"], final),
          "data": lambda: check_data(final), "feat": lambda: check_feat(final), "enc": lambda: check_enc(final), "evidence": check_evidence}[mode]()
    sys.exit(0 if ok else 1)
