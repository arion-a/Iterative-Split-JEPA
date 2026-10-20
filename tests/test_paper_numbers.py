"""The numbers stated in docs/PAPER_RESULTS.md and docs/CROSS_TRACK.md must match the raw result files."""
import glob
import json
import os

import pytest

needs = pytest.mark.skipif(not os.path.exists("results/scaling/main/2.json"), reason="results not present")


def _load(pat):
    return [json.load(open(p)) for p in sorted(glob.glob(pat))]


@needs
def test_naming_and_certificate_ranges():
    hs, sc = _load("results/handshake/main/*.json"), _load("results/scaling/main/*.json")
    assert [round(r["arms"]["main"]["naming_abs_spearman"], 3) for r in hs] == [0.848, 0.683, 0.828]
    n = [r["arms"]["main"]["naming_abs_spearman"] for r in sc]
    assert all(0.965 < x < 0.99 for x in n)                                   # B1: improved, 0.99 not reached
    for r in hs + sc:
        c = r["arms"]["main"]
        assert c["V"] <= 0.05 and c["icc"] >= 0.9 and c["L"] <= 1.02 and c["rollout_nmse"] <= 0.35
    assert min(sc[0]["pilot_stability_pairs"].values()) > 0.97 and min(hs[0]["pilot_stability_pairs"].values()) < 0.9


@needs
def test_hier_and_e36_statements():
    assert [r["RUNGS"] for r in _load("results/hier/ladder/*.json")] == [1, 1, 1]
    assert all(r["RUNGS"] == 0 for r in _load("results/hier/shuffled/*.json"))
    co = _load("results/e36/coupled_*.json"); ct = _load("results/e36/control_*.json")
    assert all(1.2 < r["closure_ratio"] < 1.4 and r["S_pass"] for r in co)
    assert all(abs(r["closure_ratio"] - 1.0) < 0.01 and r["S_pass"] for r in ct)


@pytest.mark.skipif(not os.path.exists("results/columbia_controls/2.json"), reason="results not present")
def test_columbia_statements():
    co, cc = _load("results/columbia/*.json"), _load("results/columbia_controls/*.json")
    assert all(0.85 < r["certificate"]["naming_abs_spearman"] < 0.92 for r in co)
    assert all(r["flat"] < 0.5 and r["reproduction_diff"] < 0.005 for r in cc)
