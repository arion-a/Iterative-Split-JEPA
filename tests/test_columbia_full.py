"""Data integrity and result sanity for the C2 Columbia full experiment (skip when the artefacts are absent)."""
import glob
import json
import os

import numpy as np
import pytest

D = "data/columbia_full"


@pytest.mark.skipif(not os.path.exists(f"{D}/grouping_check.json"), reason="data not prepared")
def test_grouping_and_shapes():
    g = json.load(open(f"{D}/grouping_check.json"))
    assert g["ok"] and g["best_period"] == 11 and g["pixel_break_fraction_within_videos"] <= 0.02 and g["adjacent_vs_random_distance"][0] < 0.5 * g["adjacent_vs_random_distance"][1]
    f = np.load(f"{D}/frames.npy"); a = np.load(f"{D}/audit.npz")
    assert f.shape == (100, 660, 1024) and a["total_energy"].shape == (100, 660)
    assert np.isfinite(f).all() and 0.80 < np.mean(np.isfinite(a["total_energy"]) & ~a["reject"]) < 0.95


@pytest.mark.skipif(len(glob.glob("results/columbia_full/[0-9].json")) < 3, reason="results not present")
def test_results_sanity():
    rs = [json.load(open(p)) for p in sorted(glob.glob("results/columbia_full/[0-9].json"))]
    assert [r["seed"] for r in rs] == [0, 1, 2]
    for r in rs:
        assert set(r["arms"]) == {"main", "flat", "shuffled", "temporal_only"}
        for a in r["arms"].values():
            assert all(np.isfinite(a[k]) for k in ("V", "icc", "L", "rollout_nmse", "naming_abs_spearman"))
            assert 0 <= a["naming_abs_spearman"] <= 1 and 0 <= a["icc"] <= 1.001
        assert 0 < r["tracked_energy_between_video_icc_test"] <= 1.0 and len(r["reach_psi"]) == 6
    assert len(rs[0]["seed_agreement"]) == 3
