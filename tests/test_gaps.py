"""G-study checks: depth-world arithmetic (independent of any encoder), data integrity and result sanity (skipped when artefacts are absent)."""
import glob
import json
import os

import numpy as np
import pytest
import yaml


def test_depth_world_arithmetic_supports_the_registered_mechanism():
    a = yaml.safe_load(open("configs/gaps.yaml"))["depth_world"]["a"]
    gap = lambda k, t: (1 - a[k] ** t) / (1 - a[k + 1] ** t)
    assert np.allclose([gap(k, 1) for k in range(3)], [9, 10, 10])                  # cut gaps at lag 1
    assert all(gap(k, t) > 8 for k, t in ((0, 1), (1, 4), (2, 16)))                  # clean cut at each rung's own lag of the geometric schedule
    chance = 2.0; s1_level = 0.05 * chance
    lam1 = [2 * (1 - x) for x in a]                                                  # lag-1 eigenvalues per block
    assert lam1[2] < s1_level and lam1[3] < s1_level and lam1[1] > s1_level          # at lag 1 the two slowest blocks fall below the S1 level
    assert 2 * (1 - a[2] ** 16) > s1_level                                          # ladder rung 3 (lag 16, content = blocks 3-4): lambda_max 0.30 > S1 level, so it cuts
    assert lam1[2] < s1_level                                                       # single-lag rung 3 (lag 1, same content): lambda_max 0.02 < S1 level, so it stops: at most 2 cuts


@pytest.mark.parametrize("name", ["single_pendulum", "elastic_pendulum"])
def test_system_grouping(name):
    p = f"data/{name}_full/grouping_check.json"
    if not os.path.exists(p):
        pytest.skip("not prepared")
    g = json.load(open(p))
    assert g["ok"] and g["contrast_by_period"][str(g["best_period"])] >= 0.5 and g["pixel_break_fraction_within_videos"] <= 0.02
    f = np.load(f"data/{name}_full/frames.npy"); a = np.load(f"data/{name}_full/audit.npz")
    assert f.shape[0] * g["best_period"] == g["n_clips"] and np.isfinite(f).all() and a["total_energy"].shape == f.shape[:2]


@pytest.mark.parametrize("name", ["single_pendulum", "elastic_pendulum"])
def test_system_results_sanity(name):
    fs = sorted(glob.glob(f"results/system_{name}/[0-9].json"))
    if len(fs) < 3:
        pytest.skip("results not present")
    for r in map(lambda p: json.load(open(p)), fs):
        assert set(r["arms"]) == {"main", "flat", "shuffled", "temporal_only"} and sum(r["split_sizes"]) == r["n_videos"]
        for arm in r["arms"].values():
            assert all(np.isfinite(arm[k]) for k in ("V", "icc", "L", "rollout_nmse", "naming_abs_spearman")) and 0 <= arm["naming_abs_spearman"] <= 1


def test_depth_results_sanity():
    fs = sorted(glob.glob("results/depth/[0-9].json"))
    if len(fs) < 3:
        pytest.skip("results not present")
    for r in map(lambda p: json.load(open(p)), fs):
        assert set(r["arms"]) == {"ladder", "single_lag", "shuffled"} and all(0 <= a["cuts"] <= 3 for a in r["arms"].values())
