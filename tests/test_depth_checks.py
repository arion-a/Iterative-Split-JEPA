"""Gap 3: the per-seed checks work for any number of rungs and reproduce the old two-rung verdict exactly on stored runs."""
import glob, json

import yaml

from isj.stage_b1 import CRITERIA_KEYS, criteria_keys, seed_checks

crit = yaml.safe_load(open("configs/stage_b1.yaml"))["criteria"]


def old_checks(r, c):                                   # the original two-rung formula
    r1, r2 = r["rungs"]
    return {"rung1_angle": r1["angle_deg"] < c["rung_angle_max_deg"], "rung2_angle": r2["angle_deg"] < c["rung_angle_max_deg"],
            "rung1_variant_r2": r1["variant_r2"] > c["variant_r2_min"], "rung2_variant_r2": r2["variant_r2"] > c["variant_r2_min"],
            "core_invariant_r2": r["core_invariant_r2"] > c["core_invariant_r2_min"], "nesting": r["nesting_angle_deg"] < c["nesting_angle_max_deg"],
            "rung1_gap": r1["gap_ratio"] > c["gap_ratio_min"], "rung2_gap": r2["gap_ratio"] > c["gap_ratio_min"],
            "leakage": not (r1["leak_any_significant"] or r2["leak_any_significant"]), "rank_test": not (r1["rank_deficient"] or r2["rank_deficient"])}


def test_two_rung_verdict_unchanged_on_stored_runs():
    files = glob.glob("results/stage_b1_e21/main_seed*.json")[:10]
    assert files
    for f in files:
        r = json.load(open(f))
        assert seed_checks(r, crit) == old_checks(r, crit)
    assert set(criteria_keys(2)) == set(CRITERIA_KEYS)


def test_deeper_ladders_add_checks_per_rung():
    assert {"rung3_angle", "rung3_variant_r2", "rung3_gap", "nesting3", "rung4_gap", "nesting4"} <= set(criteria_keys(4))
