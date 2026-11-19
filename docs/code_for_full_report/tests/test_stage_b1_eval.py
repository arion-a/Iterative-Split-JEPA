"""The locked B1 verdict rule, tested on synthetic results (no training)."""
import copy

import yaml

from isj.stage_b1 import evaluate

CFG = yaml.safe_load(open("configs/stage_b1.yaml"))


def good(seed=0):
    rung = lambda k: {"k": k, "angle_deg": 1.0, "variant_r2": 0.97, "gap_ratio": 500.0, "lambda_dk": 2.0,
                      "rank_deficient": False, "leak_any_significant": False}
    return {"seed": seed, "rungs": [rung(1), rung(2)], "nesting_angle_deg": 1.0, "core_invariant_r2": 0.96}


def runs_with(main):
    ctl = lambda a1, a2, g: {"seed": 0, "rungs": [{"angle_deg": a1, "gap_ratio": 500.0}, {"angle_deg": a2, "gap_ratio": g}]}
    return {"main": main, "shuffled_rung2": [ctl(1, 80, 1.0)], "rank1_rung2": [ctl(1, 40, 500.0)]}


def test_all_good_is_pass():
    ev = evaluate(runs_with([good(0), good(1), good(2)]), CFG)
    assert ev["verdict"] == "PASS" and ev["failing_criteria"] == [] and all(ev["controls"].values())


def test_texture_variant_r2_alone_is_located_risk():
    bad = copy.deepcopy(good(1)); bad["rungs"][0]["variant_r2"] = 0.4
    ev = evaluate(runs_with([good(0), bad, good(2)]), CFG)
    assert ev["verdict"] == "PASS_WITH_LOCATED_RISK" and ev["failing_criteria"] == ["rung1_variant_r2"]


def test_texture_failure_plus_anything_else_is_fail():
    bad = copy.deepcopy(good(1)); bad["rungs"][0]["variant_r2"] = 0.4; bad["rungs"][0]["angle_deg"] = 30.0
    assert evaluate(runs_with([good(0), bad, good(2)]), CFG)["verdict"] == "FAIL"


def test_category_core_is_gated():
    bad = copy.deepcopy(good(2)); bad["core_invariant_r2"] = 0.5
    ev = evaluate(runs_with([good(0), good(1), bad]), CFG)
    assert ev["verdict"] == "FAIL" and ev["failing_criteria"] == ["core_invariant_r2"]


def test_identity_variant_r2_failure_is_not_excused():
    bad = copy.deepcopy(good(0)); bad["rungs"][1]["variant_r2"] = 0.5
    assert evaluate(runs_with([bad, good(1), good(2)]), CFG)["verdict"] == "FAIL"


def test_rank_and_leakage_and_nesting_each_fail_the_run():
    for mutate in (lambda r: r["rungs"][1].__setitem__("rank_deficient", True),
                   lambda r: r["rungs"][0].__setitem__("leak_any_significant", True),
                   lambda r: r.__setitem__("nesting_angle_deg", 9.0)):
        bad = copy.deepcopy(good(0)); mutate(bad)
        assert evaluate(runs_with([bad, good(1), good(2)]), CFG)["verdict"] == "FAIL"
