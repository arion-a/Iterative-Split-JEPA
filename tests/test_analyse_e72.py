"""E72 verdict logic on made-up results (no training)."""
import json, os, sys, numpy as np
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "experiments"))
import analyse_e72 as E

def fake(K, seed, good=True, err=0.0, arm="A"):
    rho = E.rhos(K); sl = E.slow_set(K)
    pres = [0.97 if (b in sl) else 0.3 for b in range(1, K + 1)]
    if not good: pres[sl[0] - 1] = 0.5
    return {"seed": seed, "output_cov_min_eig": 0.8, "slice": {"presence": pres, "leakage_faster": [0.0] * (K - 1), "invariance_residual": [0.02] * (K - 1), "rho_hat": [r + err for r in rho]}}

def write(root, K, arm, runs):
    d = f"{root}/results/nested/e72/{arm}/K{K}_s0.5"; os.makedirs(d, exist_ok=True)
    for r in runs: json.dump(r, open(f"{d}/main_seed{r['seed']}.json", "w"))

def test_all_pass_and_fail_paths(tmp_path):
    root = str(tmp_path)
    for K in E.KS:
        write(root, K, "A", [fake(K, 290 + i, good=(i < 4 or K != 16), err=0.0) for i in range(5)] if K != 13 else [fake(K, 290 + i, err=0.05 if i < 3 else 0.0) for i in range(5)])
        write(root, K, "U", [fake(K, 290 + i, good=False, err=0.3, arm="U") for i in range(5)])
    res, lines = E.verdict(root)
    assert lines[0][1] and not lines[1][1]               # S: 5, 5, 4 passes (needs 4); R: K = 13 has 2 passes (needs 3)
    assert "K = 13: 2 of 5, required 3, short by 1" in lines[1][2]
    assert all(res[K]["O"]) and sum(res[16]["S"]) == 4 and sum(res[13]["R"]) == 2
def test_order_check():
    r = fake(11, 290); r["slice"]["rho_hat"][8], r["slice"]["rho_hat"][9] = r["slice"]["rho_hat"][9], r["slice"]["rho_hat"][8]
    assert not E.passes_order(r, 11) and E.passes_order(fake(11, 291), 11)
