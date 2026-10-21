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


@pytest.mark.skipif(not os.path.exists("results/columbia_full/2.json"), reason="results not present")
def test_columbia_full_statements():
    rs = _load("results/columbia_full/[0-9].json")
    assert all(0.90 < r["arms"]["main"]["naming_abs_spearman"] < 0.92 for r in rs)
    assert all(abs(r["arms"]["main"]["naming_abs_spearman"] - r["arms"]["temporal_only"]["naming_abs_spearman"]) < 1e-6 for r in rs)
    assert rs[0]["arms"]["flat"]["naming_abs_spearman"] > 0.5 > rs[1]["arms"]["flat"]["naming_abs_spearman"]
    assert all(0.6 < r["arms"]["main"]["icc"] < 0.75 and 0.5 < r["tracked_energy_between_video_icc_test"] < 0.6 for r in rs)
    assert all(r["arms"]["shuffled"]["naming_abs_spearman"] < r["arms"]["main"]["naming_abs_spearman"] - 0.05 for r in rs)


@pytest.mark.skipif(not os.path.exists("results/columbia_confound/2.json"), reason="results not present")
def test_confound_statements():
    for r in _load("results/columbia_confound/[0-9].json"):
        a = r["abs_spearman"]["main"]
        assert a["total_energy"] > a["kinetic_energy"] + 0.3 and a["total_energy"] > a["potential_energy"] + 0.3
        assert abs(a["amplitude"] - a["total_energy"]) < 0.02 and r["reproduction_diff"] < 0.005
        assert 0.4 < r["partial"]["psi_energy_given_amplitude"] < 0.6 and 0.4 < r["partial"]["psi_amplitude_given_energy"] < 0.6


@pytest.mark.skipif(not os.path.exists("results/depth/2.json"), reason="results not present")
def test_gap_study_statements():
    d = _load("results/depth/[0-9].json")
    assert all(r["arms"]["ladder"]["cuts"] == 3 and r["arms"]["single_lag"]["cuts"] == 2 and r["arms"]["shuffled"]["cuts"] == 0 for r in d)
    s = _load("results/system_single_pendulum/[0-9].json"); e = _load("results/system_elastic_pendulum/[0-9].json")
    assert all(0.94 < r["arms"]["main"]["naming_abs_spearman"] < 0.96 for r in s)
    assert all(0.80 < r["arms"]["main"]["naming_abs_spearman"] < 0.85 for r in e)
    assert all(r["arms"]["main"]["abs_spearman_with"]["amplitude"] < r["arms"]["main"]["naming_abs_spearman"] - 0.05 for r in s + e)
    assert all(r["arms"]["main"]["abs_spearman_with"]["z"] < 0.1 for r in e)


@pytest.mark.skipif(not os.path.exists("results/robot/2.json"), reason="results not present")
def test_other_data_statements():
    h = _load("results/hf_pendulum/[0-9].json"); r = _load("results/robot/[0-9].json")
    assert all(0.95 < x["arms"]["main"]["naming_abs_spearman"] < 0.98 and x["arms"]["main"]["abs_spearman_with"]["light_angle"] < 0.1 for x in h)
    assert all(x["arms"]["temporal_only"]["naming_abs_spearman"] < 0.2 and x["arms"]["shuffled"]["naming_abs_spearman"] > 0.95 for x in h)
    assert all(x["stop"] == "S2" and x["core_dim"] == 64 for x in h + r)                    # the ladder did not cut on either dataset
    assert all(x["r2"]["full"]["cube0"] < 0.1 for x in r)                                    # the full latent does not encode the cube
