"""H1 / R1 data integrity and result sanity (skipped when artefacts are absent)."""
import glob
import json
import os

import numpy as np
import pytest


@pytest.mark.skipif(not os.path.exists("data/hf_pendulum/audit.npz"), reason="not prepared")
def test_hf_pendulum_data():
    f = np.load("data/hf_pendulum/frames.npy"); a = np.load("data/hf_pendulum/audit.npz")
    assert f.shape == (200, 72, 1024) and np.isfinite(f).all()
    assert [int((a["split"] == s).sum()) for s in range(3)] == [140, 20, 40]
    assert np.allclose(a["kinetic"] + a["potential"], a["energy"]) and (a["energy"] > 0).all()
    assert (a["energy"][:, -1] <= a["energy"][:, 0] + 1e-6).mean() > 0.95            # damped: energy decays in (almost) every video


@pytest.mark.skipif(not os.path.exists("data/maniskill/audit.npz"), reason="not generated")
def test_maniskill_data():
    v = np.load("data/maniskill/views.npy"); a = np.load("data/maniskill/audit.npz")
    assert v.shape == (150, 2, 60, 1024) and np.isfinite(v).all()
    assert a["goal"].std(0).min() > 0.01 and a["cube"][:, 0, :2].std(0).min() > 0.005       # goal and initial cube (x, y) vary across episodes; the cube height is constant (it sits on the table)
    assert np.abs(a["cube"][:, 5:10].mean(1) - a["cube"][:, :1].mean(1)).max() < 0.05        # the cube is (nearly) still early in an episode
    assert a["tcp"].std(1).mean() > 0.01                                                    # the arm moves
    assert np.abs(v[:, 0] - v[:, 1]).mean() > 0.01                                          # the two cameras really differ


@pytest.mark.skipif(len(glob.glob("results/hf_pendulum/[0-9].json")) < 3, reason="results not present")
def test_hf_results_sanity():
    for r in map(lambda p: json.load(open(p)), sorted(glob.glob("results/hf_pendulum/[0-9].json"))):
        assert set(r["arms"]) == {"main", "flat", "shuffled", "temporal_only"} and r["split_sizes"] == [140, 20, 40]
        assert all(np.isfinite(a["naming_abs_spearman"]) and 0 <= a["naming_abs_spearman"] <= 1 for a in r["arms"].values())


@pytest.mark.skipif(len(glob.glob("results/robot/[0-9].json")) < 3, reason="results not present")
def test_robot_results_sanity():
    for r in map(lambda p: json.load(open(p)), sorted(glob.glob("results/robot/[0-9].json"))):
        assert set(r["r2"]) == {"core", "variant", "flat_top_pcs", "full"}
        assert all(np.isfinite(r["r2"]["full"][t]) and r["r2"]["full"][t] <= 1.0 for t in r["r2"]["full"])
