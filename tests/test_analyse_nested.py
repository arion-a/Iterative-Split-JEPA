"""T4: the E68/E71 verdict logic on made-up result files (before any real result exists)."""
import json, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "experiments"))
import analyse_e68_e71 as A

def fake(K, seed, presence=0.95, leak=0.02, res=0.01, health=0.9):
    return {"seed": seed, "output_cov_min_eig": health, "slice": {"presence": [presence] * K, "leakage_faster": [leak] * (K - 1), "invariance_residual": [res] * (K - 1)},
            "rungs": [{"angle_deg": 1.0, "gap_ratio": 50.0}] * (K - 1), "presence": {"mlp": [0.97] * K}}

def write(root, rel, K, seeds, **kw):
    d = f"{root}/results/nested/{rel}"; os.makedirs(d, exist_ok=True)
    for s in seeds: json.dump(fake(K, s, **kw), open(f"{d}/main_seed{s}.json", "w"))

def test_clean_and_failing_rules(tmp_path):
    assert A.slice_clean(fake(4, 1)) and not A.slice_clean(fake(4, 1, presence=0.85))
    assert "short by 0.050" in A.slice_dev(fake(4, 1, presence=0.85)) and "over by 0.150" in A.slice_dev(fake(4, 1, leak=0.25))
    assert A.all_rungs_clean(fake(11, 1)) and not A.all_rungs_clean(fake(11, 1, res=0.2))

def test_e68_verdicts(tmp_path):
    r = str(tmp_path)
    for s in (1, 2, 4, 8):
        os.makedirs(f"{r}/results/nested/e68", exist_ok=True); json.dump({"W": 1}, open(f"{r}/results/nested/e68/W_K4_s{s}.json", "w"))
        write(r, f"e68/A/s{s}", 4, range(250, 255)); write(r, f"e68/B/s{s}", 4, range(250, 255), presence=0.5)      # A clean everywhere, B nowhere
    md, verdict, b_ok, s9v = A.e68(r)
    assert verdict == "CONFIRMED" and b_ok and s9v == 8
    assert "NOT met" in "\n".join(md) and "short by" in "\n".join(md)           # line (c) fails (B minus A is negative) and says by how much
    for s in (4,): write(r, f"e68/A/s{s}", 4, range(250, 255), presence=0.5)   # now A fails at strength 4 too
    md, verdict, b_ok, s9v = A.e68(r); assert verdict == "REFUTED" and not b_ok

def test_e71_verdict(tmp_path):
    r = str(tmp_path)
    for K in (11, 13, 16):
        os.makedirs(f"{r}/results/nested/e71", exist_ok=True); json.dump({"W": 1}, open(f"{r}/results/nested/e71/W_K{K}_s0.5.json", "w"))
        write(r, f"e71/A/K{K}_s0.5", K, range(280, 285)); write(r, f"e71/U/K{K}_s0.5", K, range(280, 285))
    assert A.e71(r)[1] == "CONFIRMED"
    write(r, "e71/A/K16_s0.5", 16, range(280, 285), res=0.2)
    md, v = A.e71(r); assert v == "REFUTED" and "required 3, short by 3" in "\n".join(md)
