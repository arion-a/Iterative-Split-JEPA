"""Layered analysis (D15) for E25-E27: presence of each true block in the embedding, then separability for present blocks.
    python experiments/analyse_layered.py  -> results/enc_generality/REPORT.md
The registered rules (docs/EVIDENCE.md E25-E27) are implemented in the verdict functions below and were written before any run."""
import glob, hashlib, json, statistics as st, sys
import yaml
from isj.stage_b1 import CRITERIA_KEYS, seed_checks

L = yaml.safe_load(open("configs/layered.yaml"))
assert hashlib.sha256(json.dumps(L, sort_keys=True).encode()).hexdigest() == open("configs/layered.sha256").read().strip(), "layered criteria changed after freezing"
PRES, ABS = L["presence"]["present_min"], L["presence"]["absent_max"]
cfg = yaml.safe_load(open("configs/stage_b1.yaml")); crit = cfg["criteria"]; ctl = cfg["controls"]["must_fail"]["shuffled_rung2"]
load = lambda pat: sorted((json.load(open(f)) for f in glob.glob(pat)), key=lambda r: r["seed"])
ms = lambda v, nd=2: f"{st.mean(v):.{nd}f} ± {st.stdev(v):.{nd}f}" if len(v) > 1 else (f"{v[0]:.{nd}f}" if v else "n/a")
tab = lambda h, rows: "\n".join(["| " + " | ".join(h) + " |", "|" + "---|" * len(h)] + ["| " + " | ".join(str(c) for c in r) + " |" for r in rows])
BLOCK = ["texture", "identity", "category"]


def classify(r, k):
    """Class of rung k (block k) in one run."""
    p = r["presence"]["mlp"][k - 1]
    chk = seed_checks(r, crit)
    sep = chk[f"rung{k}_angle"] and chk[f"rung{k}_variant_r2"] and chk[f"rung{k}_gap"]
    return "ABSENT" if p < ABS else "PARTIAL" if p < PRES else ("SPLIT" if sep else "PRESENT_NOT_SEPARABLE")


def cell_table(R):
    n = len(R)
    rows = [[f"{BLOCK[b]} (block {b+1})", ms([r["presence"]["mlp"][b] for r in R], 3), ms([r["presence"]["linear"][b] for r in R], 3),
             f"{sum(r['presence']['mlp'][b] >= PRES for r in R)} of {n}"] for b in range(3)]
    cls = [[f"rung {k} ({BLOCK[k-1]})"] + [f"{sum(classify(r, k) == c for r in R)}" for c in ("ABSENT", "PARTIAL", "PRESENT_NOT_SEPARABLE", "SPLIT")] for k in (1, 2)]
    return (tab(["Block", "Presence, nonlinear probe R²", "Presence, linear R²", "Seeds present (≥ %.1f)" % PRES], rows) + "\n\n"
            + tab(["Rung", "ABSENT", "PARTIAL", "PRESENT_NOT_SEPARABLE", "SPLIT"], cls))


def present_all(R): return sum(all(p >= PRES for p in r["presence"]["mlp"]) for r in R)


def b1_rule(M, S):
    """The E23 rule: every criterion except possibly rung-1 variant R2 on at least 4 of 5 seeds; shuffled control behaves."""
    per = []
    for r in M:
        c = seed_checks(r, crit)
        c["leakage"] = max(abs(x) for rg in r["rungs"] for k, x in rg["leak_r2"].items() if k in ("rest->own", "own->rest")) < 0.01
        per.append(c)
    ok = all(sum(p[k] for p in per) >= 4 for k in CRITERIA_KEYS if k != "rung1_variant_r2")
    ctl_ok = bool(S) and st.mean(r["rungs"][1]["angle_deg"] for r in S) > ctl["rung2_angle_min_deg"] and st.mean(r["rungs"][1]["gap_ratio"] for r in S) < ctl["rung2_gap_ratio_max"]
    return ok, ctl_ok, {k: f"{sum(p[k] for p in per)}/{len(per)}" for k in CRITERIA_KEYS}


md = ["# Encoder generality: presence first, then splitting (E25-E27; criteria `configs/layered.yaml`, D15)\n"]
# ---- E25: presence at the original speeds (rhos 0.2 / 0.7 / 0.95), MLP + prediction recipe
A = load("results/stage_b1_e25/main_seed*.json")
if A:
    t_abs = sum(r["presence"]["mlp"][0] < ABS for r in A); t_pres = sum(r["presence"]["mlp"][0] >= PRES for r in A); c_pres = sum(r["presence"]["mlp"][2] >= PRES for r in A); n = len(A)
    v = "CONFIRMED" if t_abs >= 4 and c_pres >= 4 and n >= 5 else ("REFUTED" if t_pres >= 4 else "NOT CONFIRMED, NOT REFUTED (see table)")
    md += [f"## E25: is the fast (texture) block absent from the prediction-trained MLP's output at the original speeds? ({n} seeds)\n",
           f"**E25 prediction (texture presence below {ABS} on at least 4 of 5 seeds and category presence at least {PRES} on at least 4 of 5): {v}.** (texture absent on {t_abs} of {n}; texture present on {t_pres}; category present on {c_pres}). Refuted if texture presence is at least {PRES} on at least 4 of 5.\n", cell_table(A), ""]
# ---- E26: equal predictability, MLP + prediction recipe
M, S = load("results/stage_b1_e26/main_seed*.json"), load("results/stage_b1_e26/shuffled_rung2_seed*.json")
if M:
    ok, ctl_ok, counts = b1_rule(M, S); pa = present_all(M); n = len(M)
    v = "CONFIRMED" if pa >= 4 and ok and ctl_ok and n >= 5 else ("PRESENT BUT NOT SPLIT (presence holds, criteria fail)" if pa >= 4 else "NOT CONFIRMED: not all blocks present")
    md += [f"## E26: equal predictability (rhos 0.5), generic MLP + prediction recipe ({n} main, {len(S)} shuffled-control seeds)\n",
           f"**E26 prediction (all three blocks present on at least 4 of 5 seeds AND every B1 criterion except possibly rung-1 variant R² on at least 4 of 5 seeds AND shuffled control behaves): {v}.** All blocks present on {pa} of {n}; criteria rule {'held' if ok else 'failed'}; shuffled control {'behaved' if ctl_ok else 'did not behave'}.\n",
           cell_table(M), "\n" + tab(["Criterion", "Seeds passing"], [[k, c] for k, c in counts.items()]), ""]
# ---- E27: factorial, equal predictability
cells = {"mirror + paper objective": "results/stage_b1_e27/mirror_lejepa", "mlp + paper objective": "results/stage_b1_e27/mlp_lejepa",
         "mirror + prediction recipe": "results/stage_b1_e27/mirror_predict", "mlp + prediction recipe (= E26)": "results/stage_b1_e26"}
C = {k: load(p + "/main_seed*.json") for k, p in cells.items()}
if all(C.values()):
    pns = {k: sum(classify(r, kk) == "PRESENT_NOT_SEPARABLE" for r in R for kk in (1, 2)) for k, R in C.items()}
    bad = {k: sum(any(classify(r, kk) == "PRESENT_NOT_SEPARABLE" for kk in (1, 2)) for r in R) for k, R in C.items()}
    v = "CONFIRMED" if all(x < 2 for x in bad.values()) and all(len(R) >= 5 for R in C.values()) else "REFUTED"
    md += ["## E27: architecture x objective at equal predictability (main arm, 5 seeds per cell)\n",
           f"**E27 prediction (in no cell is a present block not separable on 2 or more seeds): {v}.** Seeds with a PRESENT_NOT_SEPARABLE rung, per cell: {bad}.\n"]
    for k, R in C.items(): md += [f"### {k}\n", cell_table(R), ""]
open("results/enc_generality/REPORT.md", "w").write("\n".join(md)); print("\n".join(md))
